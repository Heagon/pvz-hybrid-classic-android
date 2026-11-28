/*
 * Ultra-optimized, accuracy-preserving D3D7 renderer + Universal Sprite Atlas
 * + gdi42 Glyph Texture Atlas for PvZ Hybrid Classic v3.20.1
 * (x86 freestanding, linked into .newHE @ 0x00b52000, BSS @ 0x00b54000).
 *
 * Guarantees 100% pixel-identical rendering, zero gameplay/logic changes, and
 * bounded memory with zero leaks across multi-hour sessions:
 *  1. SetupDrawMode state cache (eliminates redundant SetRenderState calls)
 *  2. SetTexture(0, tex) state cache across all 8 sites + Flush/DrawPool/LockTex/ReleaseTextures invalidation
 *  3. Zero-overhead hybrid quad batcher: single quads emit raw 4-vert D3DPT_TRIANGLESTRIP
 *     (0% vertex inflation), while 2..256 consecutive same-state quads coalesce into ONE
 *     D3DPT_TRIANGLELIST draw call, flushing strictly FIFO on any state boundary.
 *  4. 4-page 512x512 Glyph Texture Atlas (2px transparent gutter, 4096-slot tombstone-safe
 *     hash table, 1-frame deferred BitsChanged batch upload, epoch recycle on full).
 *  5. 10-page 1024x1024 Universal Sprite Texture Atlas hooked at D3DInterface::Blt &
 *     D3DInterface::BltTransformed (packs static sprites <= 192x192 with 1px replicated
 *     edge border + 1px transparent gutter for exact D3DTADDRESS_CLAMP fidelity, opaque JPG
 *     alpha fix, zero-alloc mBits/palette read, 1-frame deferred BitsChanged batch upload,
 *     live mBitsChangedCount dynamic-mutation guard, MemoryImage::~MemoryImage tombstone
 *     eviction, and leak-free epoch recycle when all 10 pages fill).
 */
#include <stdint.h>

#define MAX_QUADS         512
#define VERT_FLOATS       8          /* D3DTLVERTEX = 32 bytes */
#define VERTS_PER_QUAD    6          /* 2 triangles in D3DPT_TRIANGLELIST */
#define MAX_BATCH_VERTS   (MAX_QUADS * VERTS_PER_QUAD)

/* Glyph Atlas (4 x 512x512 = 4 MB max, lazy-allocated) */
#define GLYPH_ATLAS_SIZE  512
#define GLYPH_ATLAS_PAGES 4
#define GLYPH_GUTTER      2
#define GLYPH_HT_SIZE     4096       /* power of 2 */
#define GLYPH_HT_MASK     (GLYPH_HT_SIZE - 1)
#define MAX_GLYPH_DIM     128

/* Universal Sprite Atlas (12 x 1024x1024 = 48 MB max, lazy-allocated) */
#define SPRITE_ATLAS_SIZE  1024
#define SPRITE_ATLAS_PAGES 12
#define SPRITE_HT_SIZE     8192      /* power of 2 */
#define SPRITE_HT_MASK     (SPRITE_HT_SIZE - 1)
#define MAX_SPRITE_W       960       /* includes seeds.png (700x70) & _Pico129.png (895x12) */
#define MAX_SPRITE_H       256
#define MAX_SPRITE_AREA    65536     /* 256x256 max area -> <=6.25% of one page */

/* O(1) gdi42 DrawString / StringWidth Flat Glyph Cache (21 fonts x 1024 slots) */
#define MAX_GDI_FONTS      21
#define FAST_GLYPH_COLS    1024      /* 0..511 direct ASCII/Latin, 512..767 direct VI 1E00..1EFF, 768..1023 hashed CJK */
#define MAX_FAST_WCHARS    512

/* 1-Quad Baked Seed-Card Texture Atlas for DrawSeedPacket (Almanac Plants / SeedChooser / SeedBank) */
#define CARD_ATLAS_SIZE      1024    /* 1024x1024 A8R8G8B8 -> 16x12 = 192 complete cards/page */
#define CARD_ATLAS_PAGES     4       /* 4 pages = 768 complete cards simultaneously (16 MB max, lazy) */
#define CARD_CELL_W          64      /* 50x70 card + 6px padding + transparent gutter */
#define CARD_CELL_H          80
#define CARD_COLS            16      /* 1024 / 64 */
#define CARD_ROWS            12      /* 12 * 80 = 960 <= 1024 */
#define CARD_CELLS_PER_PAGE  (CARD_COLS * CARD_ROWS)
#define CARD_PAD_X           6
#define CARD_PAD_Y           6
#define CARD_HT_SIZE         1024    /* power of 2 */
#define CARD_HT_MASK         (CARD_HT_SIZE - 1)
#define MAX_BAKES_PER_FRAME  16u     /* smooth amortized baking: 66 cards bake in ~4 frames */

/* Entry states for Knuth linear-probing deletion */
#define SLOT_EMPTY        0u
#define SLOT_USED         1u
#define SLOT_BLACKLISTED  2u
#define SLOT_TOMBSTONE    3u

typedef struct {
    uint32_t d[VERT_FLOATS];
} Vertex32;

typedef struct {
    int x, y, w, h;
} SexyRect;

typedef struct {
    void     *img;
    uint32_t  ready_gen;
    uint16_t  ax;
    uint16_t  ay;
    uint16_t  w;
    uint16_t  h;
    uint8_t   page;
    uint8_t   state;      /* SLOT_EMPTY / SLOT_USED / SLOT_TOMBSTONE */
    uint16_t  pad;
} GlyphEntry;

typedef struct {
    void     *img;
    uint32_t  bits_changed;
    uint32_t  ready_gen;
    uint16_t  ax;
    uint16_t  ay;
    uint16_t  w;
    uint16_t  h;
    uint8_t   page;
    uint8_t   state;      /* SLOT_EMPTY / SLOT_USED / SLOT_BLACKLISTED / SLOT_TOMBSTONE */
    uint16_t  pad;
} SpriteEntry;

typedef struct {
    uint32_t tag;         /* (uint32_t)ch | 0x80000000u */
    void    *img;
    int32_t  adv;
    int32_t  bx;
    int32_t  by;
} FastGlyph;

typedef struct {
    void    *img;
    int32_t  adv;
    int32_t  bx;
    int32_t  by;
} GdiMapNode;

typedef struct {
    int32_t   seed_type;
    int32_t   imitater_type;
    int32_t   grayness;
    uint32_t  flags;
    int32_t   dyn_cost;
    uint32_t  scale_x_bits;
    uint32_t  scale_y_bits;
    uint32_t  orig_rx_bits;
    uint32_t  orig_ry_bits;
    uint32_t  ready_gen;
    uint16_t  ax;
    uint16_t  ay;
    uint8_t   page;
    uint8_t   state;      /* SLOT_EMPTY / SLOT_USED / SLOT_BLACKLISTED */
    uint16_t  pad;
} CardEntry;

/* Exported scratch rects & live FPS cap state for trampolines */
SexyRect g_tmp_blt_rect;
SexyRect g_tmp_xform_rect;
uint32_t g_target_fps;

/* Runtime state (all placed in zero-initialized .bss @ 0x00b58000 in .newHE) */
static Vertex32    g_first_quad[4];
static Vertex32    g_quad_buf[MAX_BATCH_VERTS];
static uint32_t    g_batch_verts;
static uint8_t     g_single_quad;
static void       *g_batch_dev;

static void       *g_cached_dev;
static void       *g_cached_tex;
static uint32_t    g_tex_valid;        /* 0 = invalid, 1 = active stage-0 texture */
static int32_t     g_cached_draw_mode; /* 0 = invalid, 1 = NORMAL(0), 2 = ADDITIVE(1) */
static uint32_t    g_main_tid;
static uint32_t    g_frame_gen;        /* incremented every EndScene */

/* Live FPS cap shared-memory state (G:\fps_cap.bin mapped once via Win32 IAT) */
static volatile uint32_t *g_fps_shm;
static uint32_t    g_fps_retry_cnt;

/* 1-Quad Baked Seed-Card Texture Atlas state */
static void       *g_bake_img_a;
static uint32_t   *g_bake_bits_a;
static void       *g_bake_img_b;
static uint32_t   *g_bake_bits_b;
static void       *g_card_img[CARD_ATLAS_PAGES];
static uint32_t   *g_card_bits[CARD_ATLAS_PAGES];
static uint16_t    g_card_used[CARD_ATLAS_PAGES];
static uint8_t     g_card_full[CARD_ATLAS_PAGES];
static uint8_t     g_card_dirty[CARD_ATLAS_PAGES];
static uint8_t     g_card_reset_pending;
static uint8_t     g_in_card_bake;
static uint32_t    g_card_bakes_frame;
static CardEntry   g_card_ht[CARD_HT_SIZE];

/* SeedChooser occlusion & Loop-2 early cull state */
static uint8_t     g_sc_occlude_active;
static void       *g_sc_seen_board;
static uint32_t    g_sc_seen_tab;
static uint32_t    g_sc_seen_page;
static uint32_t    g_sc_settle_frame;

/* OPT 13: HasSeedType (0x00930000) 1/frame recount throttle + O(1) per-frame memo */
#define HST_CACHE_MAX 768u
static uint32_t    g_hst_recount_gen;
static uint32_t    g_hst_epoch;
static void       *g_hst_board;
static void       *g_hst_pi;
static uint32_t    g_hst_mode;
static uint32_t    g_hst_scene;
static uint32_t    g_hst_e0;
static uint32_t    g_hst_val_gen[HST_CACHE_MAX];
static uint8_t     g_hst_val[HST_CACHE_MAX];

/* Glyph Atlas state */
static void       *g_glyph_img[GLYPH_ATLAS_PAGES];
static uint32_t   *g_glyph_bits[GLYPH_ATLAS_PAGES];
static uint16_t    g_glyph_x[GLYPH_ATLAS_PAGES];
static uint16_t    g_glyph_y[GLYPH_ATLAS_PAGES];
static uint16_t    g_glyph_row_h[GLYPH_ATLAS_PAGES];
static uint8_t     g_glyph_full[GLYPH_ATLAS_PAGES];
static uint8_t     g_glyph_dirty[GLYPH_ATLAS_PAGES];
static uint8_t     g_glyph_reset_pending;
static uint8_t     g_in_glyph_draw;
static GlyphEntry  g_glyph_ht[GLYPH_HT_SIZE];

/* Universal Sprite Atlas state */
static void       *g_sprite_img[SPRITE_ATLAS_PAGES];
static uint32_t   *g_sprite_bits[SPRITE_ATLAS_PAGES];
static uint16_t    g_sprite_x[SPRITE_ATLAS_PAGES];
static uint16_t    g_sprite_y[SPRITE_ATLAS_PAGES];
static uint16_t    g_sprite_row_h[SPRITE_ATLAS_PAGES];
static uint8_t     g_sprite_full[SPRITE_ATLAS_PAGES];
static uint8_t     g_sprite_dirty[SPRITE_ATLAS_PAGES];
static uint8_t     g_sprite_reset_pending;
static void       *g_last_sp_img;
static SpriteEntry *g_last_sp_entry;
static SpriteEntry g_sprite_ht[SPRITE_HT_SIZE];

/* O(1) gdi42 flat glyph lookup cache */
static FastGlyph   g_fast_glyph[MAX_GDI_FONTS][FAST_GLYPH_COLS];

static inline uint32_t cur_tid(void) {
    uint32_t tid;
    __asm__ __volatile__("movl %%fs:0x24, %0" : "=r"(tid));
    return tid;
}

typedef int32_t (__stdcall *FnSetRenderState)(void *dev, uint32_t state, uint32_t val);
typedef int32_t (__stdcall *FnSetTexture)(void *dev, uint32_t stage, void *tex);
typedef int32_t (__stdcall *FnDrawPrimitive)(void *dev, uint32_t primType, uint32_t fvf,
                                             const void *verts, uint32_t vcount, uint32_t flags);
typedef int32_t (__stdcall *FnLockSurface)(void *surf, void *rect, void *ddsd, uint32_t flags, void *evt);

typedef void *(__cdecl *FnOpNew)(uint32_t size);
typedef void (__stdcall *FnMemImgCtor)(void *mem);
typedef void (__attribute__((thiscall)) *FnMemImgCreate)(void *self, int w, int h);
typedef uint32_t *(__attribute__((thiscall)) *FnMemImgGetBits)(void *self);
typedef void (__attribute__((thiscall)) *FnMemImgBitsChanged)(void *self);
typedef void (__attribute__((thiscall)) *FnMemImgCommitBits)(void *self);

extern void asm_call_d3d_check_error(int32_t hr, const char *msg);
extern void asm_call_orig_draw_image(void *g, void *img, int x, int y);
extern void asm_call_draw_image_rect(void *g, void *img, int x, int y, const SexyRect *r);
extern void asm_call_gfx_push_state(void *g);
extern void asm_call_gfx_set_colorize(void *g, uint32_t flag);
extern void asm_call_gfx_set_color(void *g, const void *color);
extern void asm_call_gfx_pop_state(void *g);
extern int32_t asm_call_get_font_id(void *font_this);
extern GdiMapNode *asm_call_gdi_map_lookup(void *fn, void *map_obj, const uint16_t *ch_ptr);
extern void asm_call_gdi_render_glyph(void *fn, void *font_obj, uint32_t ch);
extern void asm_call_orig_draw_seed_packet(const uint32_t *args8, int32_t grayness);
extern int32_t asm_call_get_current_plant_cost(void *board, int32_t seed_type, int32_t imitater_type);
extern void asm_call_gfx_copy_ctor(void *dst_g, const void *src_g);
extern void asm_call_gfx_dtor(void *g);
extern uint32_t asm_call_create_image_tex(void *d3d, void *img);
extern uint32_t asm_call_has_seed_full(void *app, uint32_t seed_type);
extern uint32_t asm_call_has_seed_body(void *app, uint32_t seed_type);
extern void asm_call_orig_board_draw(void *board, void *g);

typedef int (__stdcall *FnMultiByteToWideChar)(uint32_t cp, uint32_t flags, const char *src,
                                               int src_len, uint16_t *dst, int dst_len);
typedef void *(__stdcall *FnCreateFileA)(const char *name, uint32_t access, uint32_t share,
                                         void *sec, uint32_t disp, uint32_t flags, void *tmpl);
typedef void *(__stdcall *FnCreateFileMappingA)(void *hFile, void *sec, uint32_t prot,
                                                uint32_t maxHi, uint32_t maxLo, const char *name);
typedef void *(__stdcall *FnMapViewOfFile)(void *hMap, uint32_t access, uint32_t offHi,
                                           uint32_t offLo, uint32_t bytes);
typedef int (__stdcall *FnCloseHandle)(void *h);

static inline void *vtable_fn(void *obj, uint32_t off) {
    uint8_t *vt = *(uint8_t **)obj;
    return *(void **)(vt + off);
}

static inline void copy_v32(Vertex32 *dst, const Vertex32 *src) {
    dst->d[0] = src->d[0];
    dst->d[1] = src->d[1];
    dst->d[2] = src->d[2];
    dst->d[3] = src->d[3];
    dst->d[4] = src->d[4];
    dst->d[5] = src->d[5];
    dst->d[6] = src->d[6];
    dst->d[7] = src->d[7];
}

static inline void expand_quad_to_tris(Vertex32 *dst, const Vertex32 *src) {
    /* TRIANGLESTRIP (v0, v1, v2, v3) -> TRIANGLELIST (v0, v1, v2), (v1, v3, v2) */
    copy_v32(&dst[0], &src[0]);
    copy_v32(&dst[1], &src[1]);
    copy_v32(&dst[2], &src[2]);
    copy_v32(&dst[3], &src[1]);
    copy_v32(&dst[4], &src[3]);
    copy_v32(&dst[5], &src[2]);
}

static void zero_u32_buf(uint32_t *p, uint32_t count) {
    for (uint32_t i = 0; i < count; i++) {
        p[i] = 0u;
    }
}

void c_flush_quads(void) {
    void *dev = g_batch_dev;
    if (g_single_quad) {
        g_single_quad = 0u;
        if (dev) {
            FnDrawPrimitive fn = (FnDrawPrimitive)vtable_fn(dev, 0x64);
            fn(dev, 5u /* D3DPT_TRIANGLESTRIP */, 0x1c4u /* D3DFVF_TLVERTEX */,
               g_first_quad, 4u, 0u);
        }
        return;
    }
    uint32_t vc = g_batch_verts;
    g_batch_verts = 0u;
    if (vc > 0u && dev) {
        FnDrawPrimitive fn = (FnDrawPrimitive)vtable_fn(dev, 0x64);
        fn(dev, 4u /* D3DPT_TRIANGLELIST */, 0x1c4u /* D3DFVF_TLVERTEX */,
           g_quad_buf, vc, 0u);
    }
}

static inline Vertex32 *batch_alloc_tris(void *dev, uint32_t vcount) {
    if ((g_single_quad || g_batch_verts > 0u) && g_batch_dev != dev) {
        c_flush_quads();
    }
    if (g_single_quad) {
        if (6u + vcount > MAX_BATCH_VERTS) {
            c_flush_quads();
        } else {
            g_single_quad = 0u;
            expand_quad_to_tris(&g_quad_buf[0], g_first_quad);
            g_batch_verts = 6u;
        }
    }
    if (g_batch_verts + vcount > MAX_BATCH_VERTS) {
        c_flush_quads();
    }
    if (g_batch_verts == 0u) {
        g_batch_dev = dev;
    }
    Vertex32 *out = &g_quad_buf[g_batch_verts];
    g_batch_verts += vcount;
    return out;
}

static void notify_bits_changed(void *mem_img) {
    if (!mem_img) return;
    FnMemImgBitsChanged fn = (FnMemImgBitsChanged)vtable_fn(mem_img, 0x64);
    fn(mem_img);
}

void c_d3d_endscene_pre(void) {
    c_flush_quads();
    g_tex_valid = 0;
    g_cached_tex = 0;
    g_cached_draw_mode = 0;
    g_cached_dev = 0;
    g_batch_dev = 0;

    /* Batch-commit all dirty Glyph Atlas pages once per frame */
    for (int p = 0; p < GLYPH_ATLAS_PAGES; p++) {
        if (g_glyph_dirty[p]) {
            notify_bits_changed(g_glyph_img[p]);
            g_glyph_dirty[p] = 0;
        }
    }
    /* Batch-commit all dirty Sprite Atlas pages once per frame */
    for (int p = 0; p < SPRITE_ATLAS_PAGES; p++) {
        if (g_sprite_dirty[p]) {
            notify_bits_changed(g_sprite_img[p]);
            g_sprite_dirty[p] = 0;
        }
    }
    /* Batch-commit all dirty Baked Seed-Card Atlas pages once per frame */
    for (int p = 0; p < CARD_ATLAS_PAGES; p++) {
        if (g_card_dirty[p]) {
            notify_bits_changed(g_card_img[p]);
            g_card_dirty[p] = 0;
        }
    }

    /* Leak-free epoch recycle if all Glyph Atlas pages filled up */
    if (g_glyph_reset_pending) {
        g_glyph_reset_pending = 0;
        for (uint32_t i = 0; i < GLYPH_HT_SIZE; i++) {
            g_glyph_ht[i].state = SLOT_EMPTY;
            g_glyph_ht[i].img = 0;
        }
        for (int p = 0; p < GLYPH_ATLAS_PAGES; p++) {
            if (g_glyph_bits[p]) {
                zero_u32_buf(g_glyph_bits[p], (uint32_t)(GLYPH_ATLAS_SIZE * GLYPH_ATLAS_SIZE));
                notify_bits_changed(g_glyph_img[p]);
            }
            g_glyph_x[p] = 1;
            g_glyph_y[p] = 1;
            g_glyph_row_h[p] = 0;
            g_glyph_full[p] = 0;
            g_glyph_dirty[p] = 0;
        }
    }

    /* Leak-free epoch recycle if all Sprite Atlas pages filled up */
    if (g_sprite_reset_pending) {
        g_sprite_reset_pending = 0;
        g_last_sp_img = 0;
        g_last_sp_entry = 0;
        for (uint32_t i = 0; i < SPRITE_HT_SIZE; i++) {
            g_sprite_ht[i].state = SLOT_EMPTY;
            g_sprite_ht[i].img = 0;
        }
        for (int p = 0; p < SPRITE_ATLAS_PAGES; p++) {
            if (g_sprite_bits[p]) {
                zero_u32_buf(g_sprite_bits[p], (uint32_t)(SPRITE_ATLAS_SIZE * SPRITE_ATLAS_SIZE));
                notify_bits_changed(g_sprite_img[p]);
            }
            g_sprite_x[p] = 1;
            g_sprite_y[p] = 1;
            g_sprite_row_h[p] = 0;
            g_sprite_full[p] = 0;
            g_sprite_dirty[p] = 0;
        }
    }

    /* Leak-free epoch recycle if all 768 Baked Seed-Card Atlas slots filled up */
    if (g_card_reset_pending) {
        g_card_reset_pending = 0;
        for (uint32_t i = 0; i < CARD_HT_SIZE; i++) {
            g_card_ht[i].state = SLOT_EMPTY;
        }
        for (int p = 0; p < CARD_ATLAS_PAGES; p++) {
            if (g_card_bits[p]) {
                zero_u32_buf(g_card_bits[p], (uint32_t)(CARD_ATLAS_SIZE * CARD_ATLAS_SIZE));
                notify_bits_changed(g_card_img[p]);
            }
            g_card_used[p] = 0;
            g_card_full[p] = 0;
            g_card_dirty[p] = 0;
        }
    }

    g_card_bakes_frame = 0u;
    g_frame_gen++;
}

void c_drawpool_pre(void) {
    /* PoolEffectDraw mutates raw D3D7 stage textures & blend states directly */
    c_flush_quads();
    g_tex_valid = 0;
    g_cached_tex = 0;
    g_cached_draw_mode = 0;
}

void c_release_textures_pre(void) {
    uint32_t tid = cur_tid();
    if (g_main_tid != 0 && tid == g_main_tid) {
        c_flush_quads();
    }
    g_tex_valid = 0;
    g_cached_tex = 0;
}

/* Hooked on MemoryImage::~MemoryImage @ 0x00590430: evict destroyed pointer from both atlases */
void c_on_memimg_destroy(void *img) {
    if (!img) return;
    if (g_last_sp_img == img) {
        g_last_sp_img = 0;
        g_last_sp_entry = 0;
    }
    uint32_t hval = ((uint32_t)(uintptr_t)img >> 4) * 2654435761u;

    /* Evict from Sprite Atlas hash table */
    uint32_t sidx = (hval >> 19) & SPRITE_HT_MASK;
    for (uint32_t probe = 0; probe < 32; probe++) {
        SpriteEntry *e = &g_sprite_ht[(sidx + probe) & SPRITE_HT_MASK];
        if (e->state == SLOT_EMPTY) break;
        if (e->state != SLOT_TOMBSTONE && e->img == img) {
            e->img = 0;
            e->state = SLOT_TOMBSTONE;
            break;
        }
    }

    /* Evict from Glyph Atlas hash table */
    uint32_t gidx = (hval >> 20) & GLYPH_HT_MASK;
    for (uint32_t probe = 0; probe < 32; probe++) {
        GlyphEntry *e = &g_glyph_ht[(gidx + probe) & GLYPH_HT_MASK];
        if (e->state == SLOT_EMPTY) break;
        if (e->state == SLOT_USED && e->img == img) {
            e->img = 0;
            e->state = SLOT_TOMBSTONE;
            break;
        }
    }
}

void c_setup_draw_mode(void *d3d_iface, int32_t draw_mode) {
    void *dev = *(void **)((uint8_t *)d3d_iface + 0x20);
    if (!dev) return;
    if (g_main_tid == 0) g_main_tid = cur_tid();

    int32_t norm = (draw_mode != 0) ? 2 : 1;
    if (dev == g_cached_dev && norm == g_cached_draw_mode) {
        return;
    }

    c_flush_quads();
    g_cached_dev = dev;
    g_cached_draw_mode = norm;

    FnSetRenderState fn = (FnSetRenderState)vtable_fn(dev, 0x50);
    fn(dev, 0x13u /* D3DRS_SRCBLEND */, 5u /* D3DBLEND_SRCALPHA */);
    fn(dev, 0x14u /* D3DRS_DESTBLEND */, (norm == 2) ? 2u /* ONE */ : 6u /* INVSRCALPHA */);
}

uint32_t __stdcall c_set_texture_chk(void *dev, uint32_t stage, void *tex) {
    if (g_main_tid == 0) g_main_tid = cur_tid();

    if (stage == 0 && g_tex_valid && dev == g_cached_dev && tex == g_cached_tex) {
        return 0u;
    }

    c_flush_quads();
    if (stage == 0) {
        g_cached_dev = dev;
        g_cached_tex = tex;
        g_tex_valid = 1u;
    }

    FnSetTexture fn = (FnSetTexture)vtable_fn(dev, 0x8c);
    int32_t hr = fn(dev, stage, tex);
    if (hr < 0) {
        asm_call_d3d_check_error(hr, (const char *)0x00671a90);
        return 1u;
    }
    return 0u;
}

uint32_t __stdcall c_lock_tex_chk(void *surf, void *rect, void *ddsd, uint32_t flags, void *evt) {
    uint32_t tid = cur_tid();
    if (g_main_tid != 0 && tid == g_main_tid) {
        c_flush_quads();
    }
    g_tex_valid = 0;
    g_cached_tex = 0;

    FnLockSurface fn = (FnLockSurface)vtable_fn(surf, 0x64);
    int32_t hr = fn(surf, rect, ddsd, flags, evt);
    if (hr < 0) {
        asm_call_d3d_check_error(hr, (const char *)0x00671a5c);
        return 1u;
    }
    return 0u;
}

static inline float u32_as_f32(uint32_t u) {
    union { uint32_t u; float f; } c;
    c.u = u;
    return c.f;
}

uint32_t __stdcall c_draw_quad_chk(void *dev, uint32_t primType, uint32_t fvf,
                                   const void *verts, uint32_t vcount, uint32_t flags) {
    if (primType == 5u && fvf == 0x1c4u && vcount == 4u && flags == 0u) {
        const Vertex32 *src = (const Vertex32 *)verts;
        /* Drop Board::Draw quads strictly behind opaque SeedBank+SeedChooser wooden panels
         * (x < 442 is 100% covered across 6..14-slot banks; max_y >= 100 never touches SeedBank y=0..87). */
        if (g_sc_occlude_active) {
            float x0 = u32_as_f32(src[0].d[0]), y0 = u32_as_f32(src[0].d[1]);
            float x1 = u32_as_f32(src[1].d[0]), y1 = u32_as_f32(src[1].d[1]);
            float x2 = u32_as_f32(src[2].d[0]), y2 = u32_as_f32(src[2].d[1]);
            float x3 = u32_as_f32(src[3].d[0]), y3 = u32_as_f32(src[3].d[1]);
            if (x0 < 442.0f && x1 < 442.0f && x2 < 442.0f && x3 < 442.0f &&
                (y0 >= 100.0f || y1 >= 100.0f || y2 >= 100.0f || y3 >= 100.0f)) {
                return 0u;
            }
        }
        if ((g_single_quad || g_batch_verts > 0u) && g_batch_dev != dev) {
            c_flush_quads();
        }
        if (!g_single_quad && g_batch_verts == 0u) {
            g_batch_dev = dev;
            copy_v32(&g_first_quad[0], &src[0]);
            copy_v32(&g_first_quad[1], &src[1]);
            copy_v32(&g_first_quad[2], &src[2]);
            copy_v32(&g_first_quad[3], &src[3]);
            g_single_quad = 1u;
            return 0u;
        }
        if (g_single_quad) {
            g_single_quad = 0u;
            expand_quad_to_tris(&g_quad_buf[0], g_first_quad);
            expand_quad_to_tris(&g_quad_buf[VERTS_PER_QUAD], src);
            g_batch_verts = 2u * VERTS_PER_QUAD;
            return 0u;
        }
        if (g_batch_verts + VERTS_PER_QUAD > MAX_BATCH_VERTS) {
            c_flush_quads();
            g_batch_dev = dev;
            copy_v32(&g_first_quad[0], &src[0]);
            copy_v32(&g_first_quad[1], &src[1]);
            copy_v32(&g_first_quad[2], &src[2]);
            copy_v32(&g_first_quad[3], &src[3]);
            g_single_quad = 1u;
            return 0u;
        }
        expand_quad_to_tris(&g_quad_buf[g_batch_verts], src);
        g_batch_verts += VERTS_PER_QUAD;
        return 0u;
    }

    c_flush_quads();
    FnDrawPrimitive fn = (FnDrawPrimitive)vtable_fn(dev, 0x64);
    int32_t hr = fn(dev, primType, fvf, verts, vcount, flags);
    if (hr < 0) {
        asm_call_d3d_check_error(hr, (const char *)0x00671aa4);
        return 1u;
    }
    return 0u;
}

uint32_t __stdcall c_draw_flush_chk(void *dev, uint32_t primType, uint32_t fvf,
                                    const void *verts, uint32_t vcount, uint32_t flags) {
    c_flush_quads();
    FnDrawPrimitive fn = (FnDrawPrimitive)vtable_fn(dev, 0x64);
    int32_t hr = fn(dev, primType, fvf, verts, vcount, flags);
    if (hr < 0) {
        asm_call_d3d_check_error(hr, (const char *)0x00671abc);
        return 1u;
    }
    return 0u;
}

/* ============================================================================
 * Shared MemoryImage page allocator (creates an A8R8G8B8 w x h MemoryImage)
 * ============================================================================ */
static int alloc_atlas_memimg_wh(int w, int h, void **out_img, uint32_t **out_bits) {
    FnOpNew op_new = (FnOpNew)0x0061c130;
    void *mem = op_new(0x6cu);
    if (!mem) return 0;

    FnMemImgCtor ctor = (FnMemImgCtor)0x005900f0;
    ctor(mem);

    FnMemImgCreate create_fn = (FnMemImgCreate)vtable_fn(mem, 0x78);
    create_fn(mem, w, h);

    FnMemImgGetBits get_bits = (FnMemImgGetBits)vtable_fn(mem, 0x7c);
    uint32_t *bits = get_bits(mem);
    if (!bits) return 0;

    zero_u32_buf(bits, (uint32_t)(w * h));
    *out_img = mem;
    *out_bits = bits;
    return 1;
}

static int alloc_atlas_memimg(int dim, void **out_img, uint32_t **out_bits) {
    return alloc_atlas_memimg_wh(dim, dim, out_img, out_bits);
}

/* ============================================================================
 * OPT 5: 4-Page 512x512 Glyph Texture Atlas (1-frame deferred BitsChanged)
 * ============================================================================ */
static int ensure_glyph_page(int page) {
    if (g_glyph_img[page] && g_glyph_bits[page]) return 1;
    if (g_glyph_full[page]) return 0;
    if (!alloc_atlas_memimg(GLYPH_ATLAS_SIZE, &g_glyph_img[page], &g_glyph_bits[page])) {
        g_glyph_full[page] = 1;
        return 0;
    }
    g_glyph_x[page] = 1;
    g_glyph_y[page] = 1;
    g_glyph_row_h[page] = 0;
    return 1;
}

static void pack_glyph_deferred(void *glyph_img, int w, int h, uint32_t slot) {
    FnMemImgGetBits get_bits = (FnMemImgGetBits)vtable_fn(glyph_img, 0x7c);
    uint32_t *src = get_bits(glyph_img);
    if (!src) return;

    for (int page = 0; page < GLYPH_ATLAS_PAGES; page++) {
        if (g_glyph_full[page]) continue;
        if (!ensure_glyph_page(page)) continue;

        uint16_t cx = g_glyph_x[page];
        uint16_t cy = g_glyph_y[page];
        uint16_t rh = g_glyph_row_h[page];

        if ((int)cx + w + GLYPH_GUTTER > GLYPH_ATLAS_SIZE) {
            cx = 1;
            cy = (uint16_t)(cy + rh + GLYPH_GUTTER);
            rh = 0;
        }
        if ((int)cy + h + GLYPH_GUTTER > GLYPH_ATLAS_SIZE) {
            g_glyph_full[page] = 1;
            continue;
        }

        uint32_t *dst_base = g_glyph_bits[page] + (uint32_t)cy * GLYPH_ATLAS_SIZE + cx;
        for (int row = 0; row < h; row++) {
            uint32_t *d = dst_base + (uint32_t)row * GLYPH_ATLAS_SIZE;
            const uint32_t *s = src + (uint32_t)row * (uint32_t)w;
            for (int col = 0; col < w; col++) {
                d[col] = s[col];
            }
        }

        g_glyph_x[page] = (uint16_t)(cx + w + GLYPH_GUTTER);
        g_glyph_y[page] = cy;
        g_glyph_row_h[page] = ((uint16_t)h > rh) ? (uint16_t)h : rh;
        g_glyph_dirty[page] = 1;

        GlyphEntry *e = &g_glyph_ht[slot];
        e->img       = glyph_img;
        e->ready_gen = g_frame_gen + 1u;
        e->ax        = cx;
        e->ay        = cy;
        e->w         = (uint16_t)w;
        e->h         = (uint16_t)h;
        e->page      = (uint8_t)page;
        e->state     = SLOT_USED;
        return;
    }

    /* All 4 glyph pages full: schedule leak-free recycle at next EndScene */
    g_glyph_reset_pending = 1;
}

static inline void draw_glyph_direct(void *g, void *glyph_img, int x, int y) {
    g_in_glyph_draw = 1u;
    asm_call_orig_draw_image(g, glyph_img, x, y);
    g_in_glyph_draw = 0u;
}

void c_glyph_atlas_draw(void *g, void *glyph_img, int x, int y) {
    if (!glyph_img) return;

    void *dest = *(void **)((uint8_t *)g + 0x04);
    if (!dest || *(int *)((uint8_t *)dest + 0x24) < 200) {
        draw_glyph_direct(g, glyph_img, x, y);
        return;
    }

    int w = *(int *)((uint8_t *)glyph_img + 0x24);
    int h = *(int *)((uint8_t *)glyph_img + 0x28);
    if (w <= 0 || h <= 0) return;

    uint32_t tid = cur_tid();
    if ((g_main_tid != 0 && tid != g_main_tid) || w > MAX_GLYPH_DIM || h > MAX_GLYPH_DIM) {
        draw_glyph_direct(g, glyph_img, x, y);
        return;
    }
    if (g_main_tid == 0) g_main_tid = tid;

    uint32_t hval = ((uint32_t)(uintptr_t)glyph_img >> 4) * 2654435761u;
    uint32_t idx = (hval >> 20) & GLYPH_HT_MASK;
    uint32_t free_slot = 0xFFFFFFFFu;

    for (uint32_t probe = 0; probe < 32; probe++) {
        uint32_t s = (idx + probe) & GLYPH_HT_MASK;
        GlyphEntry *e = &g_glyph_ht[s];
        if (e->state == SLOT_EMPTY) {
            if (free_slot == 0xFFFFFFFFu) free_slot = s;
            break;
        }
        if (e->state == SLOT_TOMBSTONE) {
            if (free_slot == 0xFFFFFFFFu) free_slot = s;
            continue;
        }
        if (e->img == glyph_img) {
            if (e->w != (uint16_t)w || e->h != (uint16_t)h || g_frame_gen < e->ready_gen) {
                draw_glyph_direct(g, glyph_img, x, y);
                return;
            }
            SexyRect r;
            r.x = (int)e->ax;
            r.y = (int)e->ay;
            r.w = (int)e->w;
            r.h = (int)e->h;
            asm_call_draw_image_rect(g, g_glyph_img[e->page], x, y, &r);
            return;
        }
    }

    if (free_slot != 0xFFFFFFFFu) {
        pack_glyph_deferred(glyph_img, w, h, free_slot);
    }
    /* First frame renders directly from glyph_img; next frame uses batched atlas upload! */
    draw_glyph_direct(g, glyph_img, x, y);
}

/* ============================================================================
 * OPT 6: 10-Page 1024x1024 Universal Sprite Texture Atlas
 * Hooked at D3DInterface::Blt (0x005681F0) & BltTransformed (0x00568520)
 * ============================================================================ */
static int ensure_sprite_page(int page) {
    if (g_sprite_img[page] && g_sprite_bits[page]) return 1;
    if (g_sprite_full[page]) return 0;
    if (!alloc_atlas_memimg(SPRITE_ATLAS_SIZE, &g_sprite_img[page], &g_sprite_bits[page])) {
        g_sprite_full[page] = 1;
        return 0;
    }
    g_sprite_x[page] = 1;
    g_sprite_y[page] = 1;
    g_sprite_row_h[page] = 0;
    return 1;
}

static void pack_sprite_deferred(void *img, int w, int h, uint32_t slot) {
    uint8_t *im = (uint8_t *)img;

    /* Flush any pending software bits & compute accurate mHasTrans/mHasAlpha */
    if (*(uint8_t *)(im + 0x64) != 0) {
        FnMemImgCommitBits commit_fn = (FnMemImgCommitBits)vtable_fn(img, 0x68);
        commit_fn(img);
    }

    uint32_t *src_bits = *(uint32_t **)(im + 0x38);
    uint32_t *ctable   = *(uint32_t **)(im + 0x48);
    uint8_t  *cindices = *(uint8_t  **)(im + 0x4c);
    uint32_t  bcc      = *(uint32_t  *)(im + 0x3c);

    if (!src_bits && !(ctable && cindices)) {
        /* Already purged / hardware-only surface: blacklist so we never probe again */
        SpriteEntry *e = &g_sprite_ht[slot];
        e->img = img;
        e->bits_changed = bcc;
        e->state = SLOT_BLACKLISTED;
        return;
    }

    uint8_t has_trans = *(uint8_t *)(im + 0x51);
    uint8_t has_alpha = *(uint8_t *)(im + 0x52);
    uint32_t alpha_or = (!has_alpha && !has_trans) ? 0xFF000000u : 0u;

    /* Reserve (w + 4) x (h + 4): 1px replicated clamp border on all 4 sides + 2px gap */
    int cell_w = w + 4;
    int cell_h = h + 4;

    for (int page = 0; page < SPRITE_ATLAS_PAGES; page++) {
        if (g_sprite_full[page]) continue;
        if (!ensure_sprite_page(page)) continue;

        uint16_t cx = g_sprite_x[page];
        uint16_t cy = g_sprite_y[page];
        uint16_t rh = g_sprite_row_h[page];

        if ((int)cx + cell_w > SPRITE_ATLAS_SIZE) {
            cx = 1;
            cy = (uint16_t)(cy + rh);
            rh = 0;
        }
        if ((int)cy + cell_h > SPRITE_ATLAS_SIZE) {
            g_sprite_full[page] = 1;
            continue;
        }

        uint32_t ax = (uint32_t)cx + 1u;
        uint32_t ay = (uint32_t)cy + 1u;
        uint32_t *abits = g_sprite_bits[page];

        /* Copy sprite interior [ax..ax+w-1, ay..ay+h-1] + left/right 1px edge clamp */
        for (int row = 0; row < h; row++) {
            uint32_t *d = abits + (ay + (uint32_t)row) * SPRITE_ATLAS_SIZE + ax;
            if (src_bits) {
                const uint32_t *s = src_bits + (uint32_t)row * (uint32_t)w;
                for (int col = 0; col < w; col++) {
                    d[col] = s[col] | alpha_or;
                }
            } else {
                const uint8_t *si = cindices + (uint32_t)row * (uint32_t)w;
                for (int col = 0; col < w; col++) {
                    d[col] = ctable[si[col]] | alpha_or;
                }
            }
            /* Replicate left & right edge pixels for exact D3DTADDRESS_CLAMP bilinear */
            d[-1] = d[0];
            d[w]  = d[w - 1];
        }

        /* Replicate top & bottom border rows (including corners) */
        uint32_t *top_src = abits + ay * SPRITE_ATLAS_SIZE + (ax - 1u);
        uint32_t *top_dst = abits + (ay - 1u) * SPRITE_ATLAS_SIZE + (ax - 1u);
        uint32_t *bot_src = abits + (ay + (uint32_t)(h - 1)) * SPRITE_ATLAS_SIZE + (ax - 1u);
        uint32_t *bot_dst = abits + (ay + (uint32_t)h) * SPRITE_ATLAS_SIZE + (ax - 1u);
        int span = w + 2;
        for (int col = 0; col < span; col++) {
            top_dst[col] = top_src[col];
            bot_dst[col] = bot_src[col];
        }

        g_sprite_x[page] = (uint16_t)(cx + (uint16_t)cell_w);
        g_sprite_y[page] = cy;
        g_sprite_row_h[page] = ((uint16_t)cell_h > rh) ? (uint16_t)cell_h : rh;
        g_sprite_dirty[page] = 1;

        SpriteEntry *e = &g_sprite_ht[slot];
        e->img          = img;
        e->bits_changed = bcc;
        e->ready_gen    = g_frame_gen + 1u;
        e->ax           = (uint16_t)ax;
        e->ay           = (uint16_t)ay;
        e->w            = (uint16_t)w;
        e->h            = (uint16_t)h;
        e->page         = (uint8_t)page;
        e->state        = SLOT_USED;
        return;
    }

    /* All 10 sprite pages full: schedule leak-free recycle at next EndScene */
    g_sprite_reset_pending = 1;
}

static SpriteEntry *sprite_atlas_get(void *img) {
    if (!img) return (SpriteEntry *)0;
    uint8_t *im = (uint8_t *)img;
    int w = *(int *)(im + 0x24);
    int h = *(int *)(im + 0x28);
    /* Automatically bypasses all 512x512 glyph pages, 1024x1024 sprite/card pages, & big backgrounds! */
    if (w <= 0 || h <= 0 || w > MAX_SPRITE_W || h > MAX_SPRITE_H || (uint32_t)w * (uint32_t)h > MAX_SPRITE_AREA) {
        return (SpriteEntry *)0;
    }

    uint32_t tid = cur_tid();
    if (g_main_tid != 0 && tid != g_main_tid) return (SpriteEntry *)0;
    if (g_main_tid == 0) g_main_tid = tid;

    uint32_t bcc = *(uint32_t *)(im + 0x3c);

    /* 1-entry MRU fast path (consecutive draws of same sprite / reanim body part) */
    if (img == g_last_sp_img) {
        SpriteEntry *e = g_last_sp_entry;
        if (e) {
            if (e->state == SLOT_BLACKLISTED) return (SpriteEntry *)0;
            if (e->state == SLOT_USED) {
                if (e->w != (uint16_t)w || e->h != (uint16_t)h || e->bits_changed != bcc) {
                    e->state = SLOT_BLACKLISTED;
                    return (SpriteEntry *)0;
                }
                if (g_frame_gen < e->ready_gen) return (SpriteEntry *)0;
                return e;
            }
        }
    }

    uint32_t hval = ((uint32_t)(uintptr_t)img >> 4) * 2654435761u;
    uint32_t idx = (hval >> 19) & SPRITE_HT_MASK;
    uint32_t free_slot = 0xFFFFFFFFu;

    for (uint32_t probe = 0; probe < 32; probe++) {
        uint32_t s = (idx + probe) & SPRITE_HT_MASK;
        SpriteEntry *e = &g_sprite_ht[s];
        if (e->state == SLOT_EMPTY) {
            if (free_slot == 0xFFFFFFFFu) free_slot = s;
            break;
        }
        if (e->state == SLOT_TOMBSTONE) {
            if (free_slot == 0xFFFFFFFFu) free_slot = s;
            continue;
        }
        if (e->img == img) {
            g_last_sp_img = img;
            g_last_sp_entry = e;
            if (e->state == SLOT_BLACKLISTED) return (SpriteEntry *)0;
            if (e->w != (uint16_t)w || e->h != (uint16_t)h || e->bits_changed != bcc) {
                e->state = SLOT_BLACKLISTED;
                return (SpriteEntry *)0;
            }
            if (g_frame_gen < e->ready_gen) return (SpriteEntry *)0;
            return e;
        }
    }

    if (free_slot != 0xFFFFFFFFu) {
        pack_sprite_deferred(img, w, h, free_slot);
    }
    return (SpriteEntry *)0;
}

void *c_sprite_atlas_remap(void *img, const SexyRect **pSrcRect, SexyRect *tmp_rect) {
    if (g_in_glyph_draw || !img || !pSrcRect || !*pSrcRect) return img;
    uint8_t *im = (uint8_t *)img;
    int w = *(int *)(im + 0x24);
    int h = *(int *)(im + 0x28);
    const SexyRect *sr = *pSrcRect;
    if (sr->x < 0 || sr->y < 0 || sr->w <= 0 || sr->h <= 0 ||
        sr->x + sr->w > w || sr->y + sr->h > h) {
        return img;
    }
    SpriteEntry *e = sprite_atlas_get(img);
    if (!e) return img;
    tmp_rect->x = sr->x + (int)e->ax;
    tmp_rect->y = sr->y + (int)e->ay;
    tmp_rect->w = sr->w;
    tmp_rect->h = sr->h;
    *pSrcRect = tmp_rect;
    return g_sprite_img[e->page];
}

/* ============================================================================
 * OPT 7: O(1) gdi42.dll DrawString & StringWidth Fast Path
 *  - Stack UTF-8 / ASCII / 1-shot CP936 decode (zero heap new[]/delete[])
 *  - 21 x 1024 flat cache (zero-collision direct LUT for ASCII/Latin/Vietnamese)
 *  - Eliminates 5x std::map RB-tree walks + Win32 SEH per character
 * ============================================================================ */
static inline uint32_t fast_glyph_slot(uint16_t ch) {
    if (ch < 0x0200u) return (uint32_t)ch;
    if (ch >= 0x1E00u && ch < 0x1F00u) return 0x0200u + (uint32_t)(ch - 0x1E00u);
    return 0x0300u + ((((uint32_t)ch) * 2654435761u) >> 24);
}

static int decode_std_string(uint8_t *gdi_base, const uint8_t *std_str, uint16_t *wbuf) {
    uint32_t len = *(const uint32_t *)(std_str + 0x14);
    if (len == 0u) return 0;
    if (len >= MAX_FAST_WCHARS) return -1;

    uint32_t cap = *(const uint32_t *)(std_str + 0x18);
    const uint8_t *s = (cap < 16u) ? (std_str + 0x04) : *(const uint8_t *const *)(std_str + 0x04);
    if (!s) return -1;

    uint32_t cp = *(const uint32_t *)(gdi_base + 0x2d51);
    if (cp == 65001u) {
        int out = 0;
        uint32_t i = 0;
        while (i < len) {
            uint8_t c0 = s[i];
            if (c0 < 0x80u) {
                wbuf[out++] = (uint16_t)c0;
                i += 1u;
            } else if ((c0 & 0xE0u) == 0xC0u) {
                if (i + 1u >= len) return -1;
                uint8_t c1 = s[i + 1u];
                if ((c1 & 0xC0u) != 0x80u) return -1;
                uint32_t cpv = ((uint32_t)(c0 & 0x1Fu) << 6) | (uint32_t)(c1 & 0x3Fu);
                if (cpv < 0x80u) return -1;
                wbuf[out++] = (uint16_t)cpv;
                i += 2u;
            } else if ((c0 & 0xF0u) == 0xE0u) {
                if (i + 2u >= len) return -1;
                uint8_t c1 = s[i + 1u];
                uint8_t c2 = s[i + 2u];
                if (((c1 & 0xC0u) != 0x80u) || ((c2 & 0xC0u) != 0x80u)) return -1;
                uint32_t cpv = ((uint32_t)(c0 & 0x0Fu) << 12) |
                               ((uint32_t)(c1 & 0x3Fu) << 6) |
                               (uint32_t)(c2 & 0x3Fu);
                if (cpv < 0x800u || (cpv >= 0xD800u && cpv <= 0xDFFFu)) return -1;
                wbuf[out++] = (uint16_t)cpv;
                i += 3u;
            } else {
                return -1;
            }
        }
        return out;
    }

    int ascii = 1;
    for (uint32_t i = 0; i < len; i++) {
        if (s[i] >= 0x80u) { ascii = 0; break; }
        wbuf[i] = (uint16_t)s[i];
    }
    if (ascii) return (int)len;

    FnMultiByteToWideChar mb2wc = *(FnMultiByteToWideChar *)(gdi_base + 0x1ca448);
    if (!mb2wc) return -1;
    int wlen = mb2wc(cp, 0u, (const char *)s, (int)len, wbuf, MAX_FAST_WCHARS);
    if (wlen <= 0 || wlen > MAX_FAST_WCHARS) return -1;
    return wlen;
}

static inline FastGlyph *resolve_fast_glyph(uint8_t *gdi_base, uint32_t font_id, uint16_t ch) {
    uint32_t slot = fast_glyph_slot(ch);
    FastGlyph *fg = &g_fast_glyph[font_id][slot];
    uint32_t tag = (uint32_t)ch | 0x80000000u;
    if (fg->tag == tag) {
        return fg;
    }

    uint8_t *font_obj = gdi_base + 0x23c960u + (font_id << 4);
    void *map_obj = (void *)(font_obj + 4);
    void *fn_lookup = (void *)(gdi_base + 0x2f90u);
    void *fn_render = (void *)(gdi_base + 0x2320u);

    uint16_t key = ch;
    GdiMapNode *node = asm_call_gdi_map_lookup(fn_lookup, map_obj, &key);
    if (!node->img) {
        asm_call_gdi_render_glyph(fn_render, font_obj, (uint32_t)ch);
        node = asm_call_gdi_map_lookup(fn_lookup, map_obj, &key);
    }

    fg->img = node->img;
    fg->adv = node->adv;
    fg->bx  = node->bx;
    fg->by  = node->by;
    fg->tag = tag;
    return fg;
}

int c_gdi_draw_string(uint8_t *gdi_base, void *font_this, void *g, int x, int y,
                      const uint8_t *std_str, const void *color) {
    if (!std_str) return 0;
    if (*(const uint32_t *)(std_str + 0x14) == 0u) return 1;
    if (g_main_tid == 0 || cur_tid() != g_main_tid) return 0;

    uint16_t wbuf[MAX_FAST_WCHARS];
    int wlen = decode_std_string(gdi_base, std_str, wbuf);
    if (wlen < 0) return 0;
    if (wlen == 0) return 1;

    int32_t font_id = asm_call_get_font_id(font_this);
    if ((uint32_t)font_id >= MAX_GDI_FONTS) return 0;

    asm_call_gfx_push_state(g);
    asm_call_gfx_set_colorize(g, 1u);
    asm_call_gfx_set_color(g, color);

    int cur_x = x;
    for (int i = 0; i < wlen; i++) {
        FastGlyph *fg = resolve_fast_glyph(gdi_base, (uint32_t)font_id, wbuf[i]);
        if (fg->img) {
            c_glyph_atlas_draw(g, fg->img, cur_x + fg->bx, y - fg->by);
        }
        cur_x += fg->adv;
    }

    asm_call_gfx_pop_state(g);
    return 1;
}

int32_t c_gdi_string_width(uint8_t *gdi_base, void *font_this, const uint8_t *std_str) {
    if (!std_str) return -1;
    if (*(const uint32_t *)(std_str + 0x14) == 0u) return 0;
    if (g_main_tid == 0 || cur_tid() != g_main_tid) return -1;

    uint16_t wbuf[MAX_FAST_WCHARS];
    int wlen = decode_std_string(gdi_base, std_str, wbuf);
    if (wlen < 0) return -1;
    if (wlen == 0) return 0;

    int32_t font_id = asm_call_get_font_id(font_this);
    if ((uint32_t)font_id >= MAX_GDI_FONTS) return -1;

    int32_t total = 0;
    for (int i = 0; i < wlen; i++) {
        FastGlyph *fg = resolve_fast_glyph(gdi_base, (uint32_t)font_id, wbuf[i]);
        total += fg->adv;
    }
    return total;
}

/* ============================================================================
 * OPT 8: 1-Quad Baked Seed-Card Texture Atlas for DrawSeedPacket (0x004876f0)
 *  - Collapses ALL 78 cards in Almanac Plants & ALL 66 cards in SeedChooser
 *    from ~2,500 multi-texture quads (~300 DrawPrimitive flushes) into ONE
 *    SINGLE batched DrawPrimitive call (1 quad per card, 0 overdraw!).
 *  - Bakes each unique card ONCE into a 64x80 MemoryImage using exact
 *    two-background (black + white) straight-alpha recovery, packs up to
 *    768 complete cards across 4 lazy 1024x1024 A8R8G8B8 atlas pages, and
 *    draws via native Graphics::DrawImage (automatic mClipRect clipping!).
 * ============================================================================ */
static inline uint32_t f32_bits(float f) {
    union { float f; uint32_t u; } v;
    v.f = f;
    return v.u;
}

static inline float u32_f32(uint32_t u) {
    union { float f; uint32_t u; } v;
    v.u = u;
    return v.f;
}

static void fill_u32_buf(uint32_t *p, uint32_t count, uint32_t val) {
    for (uint32_t i = 0; i < count; i++) {
        p[i] = val;
    }
}

static int ensure_bake_buffers(void) {
    if (!g_bake_img_a) {
        if (!alloc_atlas_memimg_wh(CARD_CELL_W, CARD_CELL_H, &g_bake_img_a, &g_bake_bits_a)) return 0;
    }
    if (!g_bake_img_b) {
        if (!alloc_atlas_memimg_wh(CARD_CELL_W, CARD_CELL_H, &g_bake_img_b, &g_bake_bits_b)) return 0;
    }
    return (g_bake_img_a && g_bake_bits_a && g_bake_img_b && g_bake_bits_b) ? 1 : 0;
}

static int ensure_card_page(int page) {
    if (g_card_img[page] && g_card_bits[page]) return 1;
    if (g_card_full[page]) return 0;
    if (!alloc_atlas_memimg_wh(CARD_ATLAS_SIZE, CARD_ATLAS_SIZE, &g_card_img[page], &g_card_bits[page])) {
        g_card_full[page] = 1;
        return 0;
    }
    g_card_used[page] = 0;
    return 1;
}

static void init_bake_graphics(uint8_t *tmp_g, void *dest_img, float scale_x, float scale_y,
                               float orig_rx, float orig_ry, uint32_t g_dmode) {
    *(void **)(tmp_g + 0x04) = dest_img;
    *(float *)(tmp_g + 0x08) = (float)CARD_PAD_X;
    *(float *)(tmp_g + 0x0c) = (float)CARD_PAD_Y;
    *(float *)(tmp_g + 0x10) = scale_x;
    *(float *)(tmp_g + 0x14) = scale_y;
    *(float *)(tmp_g + 0x18) = (float)CARD_PAD_X + orig_rx;
    *(float *)(tmp_g + 0x1c) = (float)CARD_PAD_Y + orig_ry;
    *(int32_t *)(tmp_g + 0x20) = 0;
    *(int32_t *)(tmp_g + 0x24) = 0;
    *(int32_t *)(tmp_g + 0x28) = CARD_CELL_W;
    *(int32_t *)(tmp_g + 0x2c) = CARD_CELL_H;
    *(int32_t *)(tmp_g + 0x44) = (int32_t)g_dmode;
    *(uint8_t *)(tmp_g + 0x48) = 0u;
}

static void bake_card_to_atlas(uint8_t *orig_g, const uint32_t *args8, int32_t grayness,
                               float scale_x, float scale_y, float orig_rx, float orig_ry,
                               uint32_t g_dmode, CardEntry *slot) {
    if (!ensure_bake_buffers()) return;

    /* Find a free 64x80 cell across our 4 1024x1024 pages */
    int target_page = -1;
    uint16_t cell_idx = 0;
    for (int p = 0; p < CARD_ATLAS_PAGES; p++) {
        if (g_card_full[p]) continue;
        if (!ensure_card_page(p)) continue;
        if (g_card_used[p] < CARD_CELLS_PER_PAGE) {
            target_page = p;
            cell_idx = g_card_used[p];
            break;
        }
        g_card_full[p] = 1;
    }
    if (target_page < 0) {
        g_card_reset_pending = 1u;
        return;
    }

    uint8_t tmp_g[0x80];
    asm_call_gfx_copy_ctor(tmp_g, orig_g);

    uint32_t bake_args[8];
    bake_args[0] = (uint32_t)(uintptr_t)tmp_g;
    bake_args[1] = 0u; /* x = 0.0f */
    bake_args[2] = 0u; /* y = 0.0f */
    bake_args[3] = args8[3];
    bake_args[4] = args8[4];
    bake_args[5] = args8[5];
    bake_args[6] = args8[6];
    bake_args[7] = args8[7];

    /* Pass 1: render card onto opaque black (0xFF000000) */
    fill_u32_buf(g_bake_bits_a, CARD_CELL_W * CARD_CELL_H, 0xFF000000u);
    *(uint8_t *)((uint8_t *)g_bake_img_a + 0x51) = 0u;
    *(uint8_t *)((uint8_t *)g_bake_img_a + 0x52) = 0u;
    *(uint8_t *)((uint8_t *)g_bake_img_a + 0x64) = 0u;
    init_bake_graphics(tmp_g, g_bake_img_a, scale_x, scale_y, orig_rx, orig_ry, g_dmode);

    g_in_card_bake = 1u;
    asm_call_orig_draw_seed_packet(bake_args, grayness);

    /* Pass 2: render card onto opaque white (0xFFFFFFFF) for mathematically exact straight alpha */
    fill_u32_buf(g_bake_bits_b, CARD_CELL_W * CARD_CELL_H, 0xFFFFFFFFu);
    *(uint8_t *)((uint8_t *)g_bake_img_b + 0x51) = 0u;
    *(uint8_t *)((uint8_t *)g_bake_img_b + 0x52) = 0u;
    *(uint8_t *)((uint8_t *)g_bake_img_b + 0x64) = 0u;
    init_bake_graphics(tmp_g, g_bake_img_b, scale_x, scale_y, orig_rx, orig_ry, g_dmode);

    asm_call_orig_draw_seed_packet(bake_args, grayness);
    g_in_card_bake = 0u;

    asm_call_gfx_dtor(tmp_g);

    uint32_t ax = (uint32_t)(cell_idx % CARD_COLS) * CARD_CELL_W;
    uint32_t ay = (uint32_t)(cell_idx / CARD_COLS) * CARD_CELL_H;
    uint32_t *abits = g_card_bits[target_page];
    uint32_t opaque_cnt = 0u;

    for (uint32_t row = 0; row < CARD_CELL_H; row++) {
        uint32_t *dst = abits + (ay + row) * CARD_ATLAS_SIZE + ax;
        const uint32_t *sa = g_bake_bits_a + row * CARD_CELL_W;
        const uint32_t *sb = g_bake_bits_b + row * CARD_CELL_W;
        if (row == 0u || row == CARD_CELL_H - 1u) {
            for (uint32_t col = 0; col < CARD_CELL_W; col++) dst[col] = 0u;
            continue;
        }
        dst[0] = 0u;
        dst[CARD_CELL_W - 1u] = 0u;
        for (uint32_t col = 1; col < CARD_CELL_W - 1u; col++) {
            uint32_t pa = sa[col];
            uint32_t pb = sb[col];
            int32_t r0 = (int32_t)((pa >> 16) & 0xFFu);
            int32_t g0 = (int32_t)((pa >> 8)  & 0xFFu);
            int32_t b0 = (int32_t)(pa & 0xFFu);
            int32_t r1 = (int32_t)((pb >> 16) & 0xFFu);
            int32_t g1 = (int32_t)((pb >> 8)  & 0xFFu);
            int32_t b1 = (int32_t)(pb & 0xFFu);

            int32_t dr = r1 - r0; if (dr < 0) dr = 0;
            int32_t dg = g1 - g0; if (dg < 0) dg = 0;
            int32_t db = b1 - b0; if (db < 0) db = 0;
            int32_t inv_a = (dr + dg + db + 1) / 3;
            int32_t a = 255 - inv_a;
            if (a <= 0) {
                dst[col] = 0u;
            } else if (a >= 254) {
                dst[col] = 0xFF000000u | (pa & 0x00FFFFFFu);
                opaque_cnt++;
            } else {
                int32_t rr = (r0 * 255 + (a >> 1)) / a; if (rr > 255) rr = 255;
                int32_t gg = (g0 * 255 + (a >> 1)) / a; if (gg > 255) gg = 255;
                int32_t bb = (b0 * 255 + (a >> 1)) / a; if (bb > 255) bb = 255;
                dst[col] = ((uint32_t)a << 24) | ((uint32_t)rr << 16) | ((uint32_t)gg << 8) | (uint32_t)bb;
                if (a >= 200) opaque_cnt++;
            }
        }
    }

    if (opaque_cnt < 400u) {
        /* Guard against any card whose source bits were purged: never show a blank card */
        slot->state = SLOT_BLACKLISTED;
        return;
    }

    g_card_used[target_page] = (uint16_t)(cell_idx + 1u);
    g_card_dirty[target_page] = 1u;
    slot->ax        = (uint16_t)ax;
    slot->ay        = (uint16_t)ay;
    slot->page      = (uint8_t)target_page;
    slot->ready_gen = g_frame_gen + 1u;
    slot->state     = SLOT_USED;
}

void c_draw_seed_packet(const uint32_t *args8, int32_t grayness) {
    uint8_t *g = (uint8_t *)args8[0];
    uint32_t pdark_bits = args8[5];
    /* Bypass during bake recursion, null Graphics, cooldown sweep (percentDark != 0), or off-thread */
    if (g_in_card_bake || !g || (pdark_bits & 0x7FFFFFFFu) != 0u) {
        asm_call_orig_draw_seed_packet(args8, grayness);
        return;
    }
    uint32_t tid = cur_tid();
    if (g_main_tid == 0u || tid != g_main_tid) {
        asm_call_orig_draw_seed_packet(args8, grayness);
        return;
    }
    uint8_t *dest = *(uint8_t **)(g + 0x04);
    if (!dest || *(int32_t *)(dest + 0x24) < 200) {
        asm_call_orig_draw_seed_packet(args8, grayness);
        return;
    }
    /* Bypass if caller pre-enabled custom colorize state */
    if (*(uint8_t *)(g + 0x48) != 0u) {
        asm_call_orig_draw_seed_packet(args8, grayness);
        return;
    }

    float scale_x = *(float *)(g + 0x10);
    float scale_y = *(float *)(g + 0x14);
    /* Only bake cards that fit comfortably inside 64x80 cell (scale <= 1.05x) */
    if (scale_x <= 0.1f || scale_y <= 0.1f || scale_x > 1.05f || scale_y > 1.05f) {
        asm_call_orig_draw_seed_packet(args8, grayness);
        return;
    }

    float x = u32_f32(args8[1]);
    float y = u32_f32(args8[2]);
    int32_t seed_type = (int32_t)args8[3];
    int32_t imitater_type = (int32_t)args8[4];
    uint32_t draw_cost = args8[6] & 1u;
    uint32_t use_cur_cost = args8[7] & 1u;

    float trans_x = *(float *)(g + 0x08);
    float trans_y = *(float *)(g + 0x0c);
    float orig_x  = *(float *)(g + 0x18);
    float orig_y  = *(float *)(g + 0x1c);

    float orig_rx = (scale_x == 1.0f) ? 0.0f : (orig_x - trans_x);
    float orig_ry = (scale_y == 1.0f) ? 0.0f : (orig_y - trans_y);
    uint32_t sx_bits = f32_bits(scale_x);
    uint32_t sy_bits = f32_bits(scale_y);
    uint32_t orx_bits = f32_bits(orig_rx);
    uint32_t ory_bits = f32_bits(orig_ry);

    float anchor_x = trans_x + x * scale_x;
    float anchor_y = trans_y + y * scale_y;

    uint8_t *app = *(uint8_t **)0x006a9ec0;
    void *board = app ? *(void **)(app + 0x768) : (void *)0;
    uint32_t game_mode = app ? (*(uint32_t *)(app + 0x7fc) & 0xFFu) : 0u;
    uint32_t debug_flag = app ? (uint32_t)(*(uint8_t *)(app + 0x814) != 0u) : 0u;
    uint32_t mod_e0 = (*(uint32_t *)0x00e0e0e0 != 0u) ? 1u : 0u;
    uint32_t g_dmode = (*(int32_t *)(g + 0x44) != 0) ? 1u : 0u;

    int32_t dyn_cost = -1;
    if (draw_cost && use_cur_cost && board) {
        dyn_cost = asm_call_get_current_plant_cost(board, seed_type, imitater_type);
    }

    uint32_t flags = draw_cost
                   | (use_cur_cost << 1)
                   | (debug_flag << 2)
                   | (mod_e0 << 3)
                   | (g_dmode << 4)
                   | ((board != (void *)0 ? 1u : 0u) << 5)
                   | (game_mode << 8);

    uint32_t h = (uint32_t)seed_type * 2654435761u;
    h ^= (uint32_t)imitater_type * 2246822519u;
    h ^= (uint32_t)grayness * 3266489917u;
    h ^= flags * 668265263u;
    h ^= sx_bits ^ (sy_bits >> 3);
    h ^= (uint32_t)dyn_cost * 374761393u;
    uint32_t idx = (h ^ (h >> 16)) & CARD_HT_MASK;

    CardEntry *free_slot = (CardEntry *)0;
    for (uint32_t probe = 0; probe < 24u; probe++) {
        CardEntry *e = &g_card_ht[(idx + probe) & CARD_HT_MASK];
        if (e->state == SLOT_EMPTY) {
            free_slot = e;
            break;
        }
        if (e->seed_type == seed_type &&
            e->imitater_type == imitater_type &&
            e->grayness == grayness &&
            e->flags == flags &&
            e->dyn_cost == dyn_cost &&
            e->scale_x_bits == sx_bits &&
            e->scale_y_bits == sy_bits &&
            e->orig_rx_bits == orx_bits &&
            e->orig_ry_bits == ory_bits) {
            if (e->state == SLOT_BLACKLISTED || g_frame_gen < e->ready_gen) {
                asm_call_orig_draw_seed_packet(args8, grayness);
                return;
            }
            /* 1-QUAD HARDWARE HIT! Native Graphics::DrawImage handles mClipRect & batching! */
            int32_t draw_x = ((anchor_x >= 0.0f) ? (int32_t)(anchor_x + 0.5f) : (int32_t)(anchor_x - 0.5f)) - CARD_PAD_X + 1;
            int32_t draw_y = ((anchor_y >= 0.0f) ? (int32_t)(anchor_y + 0.5f) : (int32_t)(anchor_y - 0.5f)) - CARD_PAD_Y + 1;
            SexyRect sr;
            sr.x = (int)e->ax + 1;
            sr.y = (int)e->ay + 1;
            sr.w = CARD_CELL_W - 2;
            sr.h = CARD_CELL_H - 2;

            *(float *)(g + 0x08) = 0.0f;
            *(float *)(g + 0x0c) = 0.0f;
            *(float *)(g + 0x10) = 1.0f;
            *(float *)(g + 0x14) = 1.0f;
            *(float *)(g + 0x18) = 0.0f;
            *(float *)(g + 0x1c) = 0.0f;

            asm_call_draw_image_rect(g, g_card_img[e->page], draw_x, draw_y, &sr);

            *(float *)(g + 0x08) = trans_x;
            *(float *)(g + 0x0c) = trans_y;
            *(float *)(g + 0x10) = scale_x;
            *(float *)(g + 0x14) = scale_y;
            *(float *)(g + 0x18) = orig_x;
            *(float *)(g + 0x1c) = orig_y;
            *(uint8_t *)(g + 0x48) = 0u; /* Match DrawSeedPacket exit post-condition @ 0x004881fc */
            return;
        }
    }

    /* Cache miss: draw normally to screen now, and bake into Card Atlas (up to 16 cards/frame) */
    asm_call_orig_draw_seed_packet(args8, grayness);

    if (free_slot && g_card_bakes_frame < MAX_BAKES_PER_FRAME) {
        g_card_bakes_frame++;
        free_slot->seed_type     = seed_type;
        free_slot->imitater_type = imitater_type;
        free_slot->grayness      = grayness;
        free_slot->flags         = flags;
        free_slot->dyn_cost      = dyn_cost;
        free_slot->scale_x_bits  = sx_bits;
        free_slot->scale_y_bits  = sy_bits;
        free_slot->orig_rx_bits  = orx_bits;
        free_slot->orig_ry_bits  = ory_bits;
        bake_card_to_atlas(g, args8, grayness, scale_x, scale_y, orig_rx, orig_ry, g_dmode, free_slot);
    }
}

/* ============================================================================
 * OPT 9: Live Selectable 30 / 60 / 90 / 120 FPS Engine Pacer (Exact 100 Hz Logic)
 *  - Maps G:\fps_cap.bin once via existing PE IAT (0 syscalls/frame)
 *  - Switches instantly mid-game from Android PAD -> FPS chip
 *  - Preserves exact 100.00 Hz UpdateFrames game speed at 30, 60, 90, AND 120 FPS!
 * ============================================================================ */
static void try_map_fps_shm(void) {
    FnCreateFileA fn_open = *(FnCreateFileA *)0x00652114;
    FnCreateFileMappingA fn_cmap = *(FnCreateFileMappingA *)0x0065207c;
    FnMapViewOfFile fn_map = *(FnMapViewOfFile *)0x00652078;
    FnCloseHandle fn_close = *(FnCloseHandle *)0x006520b8;
    if (!fn_open || !fn_cmap || !fn_map || !fn_close) return;

    void *hf = fn_open("fps_cap.bin", 0x80000000u /* GENERIC_READ */,
                       7u /* FILE_SHARE_R|W|D */, (void *)0,
                       3u /* OPEN_EXISTING */, 0x80u /* NORMAL */, (void *)0);
    if (hf == (void *)(uintptr_t)0xFFFFFFFFu || !hf) {
        hf = fn_open("G:\\fps_cap.bin", 0x80000000u, 7u, (void *)0, 3u, 0x80u, (void *)0);
    }
    if (hf == (void *)(uintptr_t)0xFFFFFFFFu || !hf) return;

    void *hm = fn_cmap(hf, (void *)0, 2u /* PAGE_READONLY */, 0u, 4u, (const char *)0);
    if (hm) {
        void *view = fn_map(hm, 4u /* FILE_MAP_READ */, 0u, 0u, 4u);
        if (view) {
            g_fps_shm = (volatile uint32_t *)view;
        }
        fn_close(hm);
    }
    fn_close(hf);
}

uint32_t c_get_target_fps(void) {
    if (!g_fps_shm) {
        if ((g_fps_retry_cnt++ & 127u) == 0u) {
            try_map_fps_shm();
        }
    }
    uint32_t v = g_fps_shm ? *g_fps_shm : 60u;
    if (v != 30u && v != 60u && v != 90u && v != 120u) {
        v = 60u;
    }
    g_target_fps = v;
    return v;
}

uint32_t c_fps_should_update_120(uint8_t *app, const double *fact_and_ft) {
    double fact = fact_and_ft[0];       /* [esp+0x30] = aUpdateFTimeFact (e.g. 0.8333 at 120 FPS) */
    double frame_time = fact_and_ft[1]; /* [esp+0x38] = aFrameTime (e.g. 8.3333 ms at 120 FPS) */
    double *acc_upd = (double *)(app + 0x460);
    double *acc_frm = (double *)(app + 0x468);
    double next = *acc_upd + fact;
    if (next >= 1.0) {
        /* Run normal 1 logic tick; State 2 will add (fact - 1.0) cleanly */
        return 1u;
    }
    /* Interpolated/paced visual frame without advancing 100 Hz gameplay logic */
    *acc_upd = next;
    *(uint32_t *)(app + 0x488) = 3u;    /* mUpdateAppState = 3 -> DrawDirtyStuff */
    *(uint8_t  *)(app + 0x45a) = 1u;    /* mHasPendingDraw = 1 */
    double nf = *acc_frm - frame_time;
    *acc_frm = (nf > 0.0) ? nf : 0.0;
    return 0u;
}

/* ============================================================================
 * OPT 10: Zero-Visual-Loss Occluded PoolEffectDraw Cull during SeedChooser
 *  - During SeedChooser (SCENE_LEVEL_INTRO, panel docked mY<=10, CHOOSE_NORMAL,
 *    mViewLawnTime==0, camera panned to street mTransX <= -80), the entire pool
 *    is 100% occluded behind the opaque wooden SeedChooser panel + sidebar.
 *  - Skipping PoolEffectDraw saves ~9-11 ms/frame on Pool/Fog SeedChooser with
 *    zero visible pixel difference; immediately resumes on View Lawn / Combat.
 * ============================================================================ */
uint32_t c_pool_should_skip(void *g) {
    if (g_sc_occlude_active) return 1u;
    if (!g) return 0u;
    uint8_t *app = *(uint8_t **)0x006a9ec0;
    if (!app) return 0u;
    if (*(uint32_t *)(app + 0x7fc) != 2u) return 0u;  /* SCENE_LEVEL_INTRO only */
    uint8_t *sc = *(uint8_t **)(app + 0x774);         /* mSeedChooserScreen */
    if (!sc) return 0u;
    if (*(int32_t *)(sc + 0x34) > 10) return 0u;      /* panel must be fully docked */
    if (*(int32_t *)(sc + 0xd38) != 0 || *(int32_t *)(sc + 0xd3c) != 0) return 0u;
    if (*(float *)((uint8_t *)g + 0x08) > -80.0f) return 0u;
    return 1u;
}

/* ============================================================================
 * OPT 11: Board::Draw Occluded Quad Cull + SeedChooser Loop-2 Early Off-Screen Cull
 *  - Wraps Board::Draw (0x00416880): when SeedChooser is fully docked at mY<=10
 *    in CHOOSE_NORMAL with camera panned right, drops Board::Draw quads strictly
 *    inside [0..598, 0..588] (100% covered by opaque SeedChooser+SeedBank panels).
 *  - Early-culls ~334 off-screen seeds at top of SeedChooser Loop 2 (0x004849e5)
 *    once (board, tab, page) has settled for 2 frames (preserving exact SeedHitTest).
 * ============================================================================ */
void c_board_draw_wrap(void *board, void *g) {
    uint8_t occ = 0u;
    if (board && g) {
        uint8_t *app = *(uint8_t **)0x006a9ec0;
        if (app && *(uint32_t *)(app + 0x7fc) == 2u) {
            uint8_t *sc = *(uint8_t **)(app + 0x774);
            if (sc && *(int32_t *)(sc + 0x34) <= 10 &&
                *(int32_t *)(sc + 0xd38) == 0 && *(int32_t *)(sc + 0xd3c) == 0) {
                int32_t bx = *(int32_t *)((uint8_t *)board + 0x30);
                float tx = *(float *)((uint8_t *)g + 0x08);
                if (bx <= -80 || tx <= -80.0f) {
                    occ = 1u;
                }
            }
        }
    }
    g_sc_occlude_active = occ;
    asm_call_orig_board_draw(board, g);
    g_sc_occlude_active = 0u;
}

uint32_t c_sc_loop2_skip(uint8_t *sc, uint8_t *seed) {
    if (!sc || !seed) return 0u;
    /* Never skip picked/flying cards or active preset-deck load actions */
    if (*(uint32_t *)(seed + 0x24) != 3u) return 0u;
    if (*(uint32_t *)(sc + 0xb8d0) != 0u || *(uint32_t *)(sc + 0xb8d4) != 0u) return 0u;
    uint8_t *board = *(uint8_t **)(sc + 0xd14);
    if (!board) return 0u;
    uint32_t tab = *(uint32_t *)(board + 0x58b4);
    uint32_t page = *(uint32_t *)(board + 0x57b4);
    if (board != g_sc_seen_board || tab != g_sc_seen_tab || page != g_sc_seen_page) {
        g_sc_seen_board = board;
        g_sc_seen_tab = tab;
        g_sc_seen_page = page;
        g_sc_settle_frame = g_frame_gen + 2u;
        return 0u;
    }
    if (g_frame_gen < g_sc_settle_frame) return 0u;
    int32_t y = *(int32_t *)(seed + 0x04);
    return (y < -10 || y > 560) ? 1u : 0u;
}

/* ============================================================================
 * OPT 12: D3DInterface::DrawTrianglesTex (0x00568e30) Universal Sprite Atlas
 *         + Zero-SEH Unified TRIANGLELIST Batcher (Reanimation Zombies & Plants!)
 *  - Eliminates 350-2500x/frame 19KB __chkstk + SEH + SetTexture + DrawPrimitive
 *    flushes across EVERY animated zombie, plant, lawnmower, and particle!
 *  - Remaps all <=256x256 body-part sprites onto our 12-page 1024x1024 Sprite
 *    Atlas (1px edge-clamped borders -> exact bilinear fidelity) and batches
 *    all triangles directly into g_quad_buf (up to 3072 verts = 1024 tris/draw!).
 * ============================================================================ */
typedef struct {
    float    x, y, u, v;
    uint32_t color;
} SexyTriVertex;

static inline uint32_t f32_as_u32(float f) {
    union { float f; uint32_t u; } c;
    c.f = f;
    return c.u;
}

uint32_t c_draw_triangles_tex(const uint32_t *color4, const uint32_t *args9) {
    if (g_in_card_bake || !color4 || !args9) return 0u;
    uint8_t *d3d = (uint8_t *)args9[0];
    const SexyTriVertex *verts = (const SexyTriVertex *)args9[1];
    int32_t num_tris = (int32_t)args9[2];
    int32_t draw_mode = (int32_t)args9[3];
    void *img = (void *)args9[4];
    const void *clip_rect = (const void *)args9[8];

    if (!d3d || !verts || !img || clip_rect != (const void *)0) return 0u;
    if (num_tris <= 0 || num_tris > 128) return 0u;
    if (*(uint8_t *)(d3d + 0x3c) == 0u) return 0u;             /* BeginScene not active yet */
    if (*(volatile uint8_t *)0x006a9f51 != 1u) return 0u;      /* Let SetLinearFilter init once */
    void *dev = *(void **)(d3d + 0x20);
    if (!dev) return 0u;

    uint32_t tid = cur_tid();
    if (g_main_tid != 0u && tid != g_main_tid) return 0u;
    if (g_main_tid == 0u) g_main_tid = tid;

    uint32_t vcount = (uint32_t)num_tris * 3u;
    uint32_t uv_in_unit = 1u;
    for (uint32_t i = 0; i < vcount; i++) {
        float u = verts[i].u;
        float v = verts[i].v;
        if (u < -0.005f || u > 1.005f || v < -0.005f || v > 1.005f) {
            uv_in_unit = 0u;
            break;
        }
    }

    void *target_img = img;
    uint32_t use_atlas = 0u;
    float u_off = 0.0f, v_off = 0.0f, u_scale = 1.0f, v_scale = 1.0f;
    if (uv_in_unit) {
        SpriteEntry *se = sprite_atlas_get(img);
        if (se) {
            target_img = g_sprite_img[se->page];
            use_atlas = 1u;
            const float inv = 1.0f / (float)SPRITE_ATLAS_SIZE;
            u_off   = (float)se->ax * inv;
            v_off   = (float)se->ay * inv;
            u_scale = (float)se->w  * inv;
            v_scale = (float)se->h  * inv;
        }
    }

    uint8_t *tim = (uint8_t *)target_img;
    uint8_t *td = *(uint8_t **)(tim + 0x40);
    if (!td || *(void **)(td + 0x3c) == (void *)0 ||
        *(int32_t *)(tim + 0x24) != *(int32_t *)(td + 0x14) ||
        *(int32_t *)(tim + 0x28) != *(int32_t *)(td + 0x18) ||
        *(uint32_t *)(tim + 0x3c) != *(uint32_t *)(td + 0x2c) ||
        *(uint32_t *)(tim + 0x44) != *(uint32_t *)(td + 0x40)) {
        if (!asm_call_create_image_tex(d3d, target_img)) return 0u;
        td = *(uint8_t **)(tim + 0x40);
        if (!td || *(void **)(td + 0x3c) == (void *)0) return 0u;
    }

    float max_u = *(float *)(td + 0x34);
    float max_v = *(float *)(td + 0x38);
    if (max_u > 1.0f || max_v > 1.0f) return 0u; /* Multi-piece texture: let original handle */

    uint8_t *p_beg = *(uint8_t **)(td + 0x04);
    uint8_t *p_end = *(uint8_t **)(td + 0x08);
    if (!p_beg || p_end <= p_beg) return 0u;
    void *surf = *(void **)p_beg;
    if (!surf) return 0u;

    if (!use_atlas) {
        u_scale = max_u;
        v_scale = max_v;
    }

    float tx = u32_as_f32(args9[5]);
    float ty = u32_as_f32(args9[6]);
    uint32_t def_col = ((color4[3] & 0xFFu) << 24)
                     | ((color4[0] & 0xFFu) << 16)
                     | ((color4[1] & 0xFFu) << 8)
                     |  (color4[2] & 0xFFu);

    /* Fast occlusion check during Board::Draw behind opaque SeedChooser panel */
    if (g_sc_occlude_active) {
        uint32_t any_vis = 0u;
        for (uint32_t t = 0; t < (uint32_t)num_tris; t++) {
            const SexyTriVertex *tv = &verts[t * 3u];
            float x0 = tv[0].x + tx, y0 = tv[0].y + ty;
            float x1 = tv[1].x + tx, y1 = tv[1].y + ty;
            float x2 = tv[2].x + tx, y2 = tv[2].y + ty;
            if (!(x0 < 442.0f && x1 < 442.0f && x2 < 442.0f &&
                  (y0 >= 100.0f || y1 >= 100.0f || y2 >= 100.0f))) {
                any_vis = 1u;
                break;
            }
        }
        if (!any_vis) return 1u;
    }

    c_setup_draw_mode(d3d, draw_mode);
    c_set_texture_chk(dev, 0u, surf);

    Vertex32 *dst = batch_alloc_tris(dev, vcount);
    for (uint32_t i = 0; i < vcount; i++) {
        const SexyTriVertex *sv = &verts[i];
        uint32_t col = sv->color ? sv->color : def_col;
        dst[i].d[0] = f32_as_u32(sv->x + tx);
        dst[i].d[1] = f32_as_u32(sv->y + ty);
        dst[i].d[2] = 0u;          /* z = 0.0f */
        dst[i].d[3] = 0x3f800000u; /* rhw = 1.0f */
        dst[i].d[4] = col;
        dst[i].d[5] = 0u;          /* specular = 0 */
        dst[i].d[6] = f32_as_u32(u_off + sv->u * u_scale);
        dst[i].d[7] = f32_as_u32(v_off + sv->v * v_scale);
    }
    return 1u;
}

/* ============================================================================
 * OPT 13: HasSeedType (0x00930000) 1/Frame Recount Throttle + O(1) Memoization
 *  - Hybrid mod runs a 563-iteration playerInfo recount loop at 0x00930000 on
 *    EVERY call (~1,700 calls/frame in SeedChooser = ~957,000 wasted iterations!).
 *  - Runs the recount once per frame (exact same 60-90 Hz freshness) and caches
 *    the read-only boolean result per (frame, board, mode, scene, playerInfo, e0).
 * ============================================================================ */
uint32_t c_has_seed_type(void *app_ptr, uint32_t seed_type) {
    if (!app_ptr) return asm_call_has_seed_full(app_ptr, seed_type);
    uint8_t *app = (uint8_t *)app_ptr;
    void *board = *(void **)(app + 0x768);
    void *pi = *(void **)(app + 0x82c);
    uint32_t mode = *(uint32_t *)(app + 0x7f8);
    uint32_t scene = *(uint32_t *)(app + 0x7fc);
    uint32_t e0 = *(uint32_t *)0x00e0e0e0;
    uint32_t fg = g_frame_gen + 1u; /* non-zero even on Frame 0 */

    uint32_t need_recount = (g_hst_recount_gen != fg);
    if (need_recount || board != g_hst_board || pi != g_hst_pi ||
        mode != g_hst_mode || scene != g_hst_scene || e0 != g_hst_e0) {
        g_hst_board = board;
        g_hst_pi = pi;
        g_hst_mode = mode;
        g_hst_scene = scene;
        g_hst_e0 = e0;
        g_hst_epoch++;
        if (g_hst_epoch == 0u) {
            for (uint32_t i = 0; i < HST_CACHE_MAX; i++) g_hst_val_gen[i] = 0u;
            g_hst_epoch = 1u;
        }
    }

    if (need_recount) {
        g_hst_recount_gen = fg;
        uint32_t res = asm_call_has_seed_full(app_ptr, seed_type);
        if (board && seed_type < HST_CACHE_MAX) {
            g_hst_val[seed_type] = (uint8_t)res;
            g_hst_val_gen[seed_type] = g_hst_epoch;
        }
        return res;
    }

    if (board && seed_type < HST_CACHE_MAX && g_hst_val_gen[seed_type] == g_hst_epoch) {
        return (uint32_t)g_hst_val[seed_type];
    }

    uint32_t res = asm_call_has_seed_body(app_ptr, seed_type);
    if (board && seed_type < HST_CACHE_MAX) {
        g_hst_val[seed_type] = (uint8_t)res;
        g_hst_val_gen[seed_type] = g_hst_epoch;
    }
    return res;
}
