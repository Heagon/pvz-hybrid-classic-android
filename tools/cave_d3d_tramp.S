.intel_syntax noprefix
.section .text.entry, "ax"

/* =====================================================================
 * Fixed entry jump table @ VA 0x00b52000 (each slot = 8 bytes):
 *   0x00b52000 (+0x00): _entry_glyph_atlas_draw  (called from gdi42.dll!)
 *   0x00b52008 (+0x08): _entry_setup_draw_mode   (jmp from 0x005681a0)
 *   0x00b52010 (+0x10): _entry_set_texture_chk   (call from 8 SetTexture sites)
 *   0x00b52018 (+0x18): _entry_draw_quad_chk     (call from 3 quad DrawPrimitive sites)
 *   0x00b52020 (+0x20): _entry_draw_flush_chk    (call from 6 other DrawPrimitive sites)
 *   0x00b52028 (+0x28): _entry_flush_linfilt     (call from 0x005661bb)
 *   0x00b52030 (+0x30): _entry_flush_drawpool    (call from 0x0046a606)
 *   0x00b52038 (+0x38): _entry_d3d_flush         (jmp from 0x00568ec0)
 *   0x00b52040 (+0x40): _entry_release_textures  (jmp from 0x00565a10)
 *   0x00b52048 (+0x48): _entry_lock_tex_chk      (call from 2 Lock Texture sites)
 *   0x00b52050 (+0x50): _entry_d3d_blt           (jmp from 0x005681f0)
 *   0x00b52058 (+0x58): _entry_d3d_blt_xform     (jmp from 0x00568520)
 *   0x00b52060 (+0x60): _entry_memimg_dtor       (jmp from 0x00590430)
 *   0x00b52068 (+0x68): _entry_create_image_tex  (jmp from 0x00567cf0 zero-SEH fast path)
 *   0x00b52070 (+0x70): _entry_d3d_check_error   (jmp from 0x005644e0 zero-SEH fast path)
 *   0x00b52078 (+0x78): _entry_gdi_draw_string   (jmp from gdi42 DrawString trampoline)
 *   0x00b52080 (+0x80): _entry_gdi_string_width  (jmp from gdi42 StringWidth trampoline)
 *   0x00b52088 (+0x88): _entry_set_linfilt       (jmp from 0x005661b0: always-LINEAR filter lock)
 *   0x00b52090 (+0x90): _entry_draw_seed_packet  (jmp from 0x004876f0: Display-List cache)
 *   0x00b52098 (+0x98): _entry_fps_pace          (jmp from 0x00551ac7: live 30/60/90/120 FPS cap)
 *   0x00b520a0 (+0xa0): _entry_fps_gate          (jmp from 0x00551e18: exact 100Hz gate for 120FPS)
 *   0x00b520a8 (+0xa8): _entry_pool_draw         (jmp from 0x00469de0: occluded SeedChooser pool cull)
 *   0x00b520b0 (+0xb0): _entry_board_draw        (jmp from 0x00416880: occluded SeedChooser quad cull)
 *   0x00b520b8 (+0xb8): _entry_sc_loop2_cull     (jmp from 0x004849e5: SeedChooser Loop-2 early cull)
 *   0x00b520c0 (+0xc0): _entry_draw_triangles_tex (jmp from 0x00568e30: Reanim Sprite Atlas + batcher)
 *   0x00b520c8 (+0xc8): _entry_has_seed_type     (jmp from 0x00930000: HasSeedType 1/frame cache)
 * ===================================================================== */

.globl _entry_glyph_atlas_draw
_entry_glyph_atlas_draw:
    jmp     _tramp_glyph_atlas_draw
    .align  8, 0x90

.globl _entry_setup_draw_mode
_entry_setup_draw_mode:
    jmp     _tramp_setup_draw_mode
    .align  8, 0x90

.globl _entry_set_texture_chk
_entry_set_texture_chk:
    jmp     _c_set_texture_chk@12
    .align  8, 0x90

.globl _entry_draw_quad_chk
_entry_draw_quad_chk:
    jmp     _c_draw_quad_chk@24
    .align  8, 0x90

.globl _entry_draw_flush_chk
_entry_draw_flush_chk:
    jmp     _c_draw_flush_chk@24
    .align  8, 0x90

.globl _entry_flush_linfilt
_entry_flush_linfilt:
    jmp     _tramp_flush_linfilt
    .align  8, 0x90

.globl _entry_flush_drawpool
_entry_flush_drawpool:
    jmp     _tramp_flush_drawpool
    .align  8, 0x90

.globl _entry_d3d_flush
_entry_d3d_flush:
    jmp     _tramp_d3d_flush
    .align  8, 0x90

.globl _entry_release_textures
_entry_release_textures:
    jmp     _tramp_release_textures
    .align  8, 0x90

.globl _entry_lock_tex_chk
_entry_lock_tex_chk:
    jmp     _c_lock_tex_chk@20
    .align  8, 0x90

.globl _entry_d3d_blt
_entry_d3d_blt:
    jmp     _tramp_d3d_blt
    .align  8, 0x90

.globl _entry_d3d_blt_xform
_entry_d3d_blt_xform:
    jmp     _tramp_d3d_blt_xform
    .align  8, 0x90

.globl _entry_memimg_dtor
_entry_memimg_dtor:
    jmp     _tramp_memimg_dtor
    .align  8, 0x90

.globl _entry_create_image_tex
_entry_create_image_tex:
    jmp     _tramp_create_image_tex
    .align  8, 0x90

.globl _entry_d3d_check_error
_entry_d3d_check_error:
    jmp     _tramp_d3d_check_error
    .align  8, 0x90

.globl _entry_gdi_draw_string
_entry_gdi_draw_string:
    jmp     _tramp_gdi_draw_string
    .align  8, 0x90

.globl _entry_gdi_string_width
_entry_gdi_string_width:
    jmp     _tramp_gdi_string_width
    .align  8, 0x90

.globl _entry_set_linfilt
_entry_set_linfilt:
    jmp     _tramp_set_linfilt
    .align  8, 0x90

.globl _entry_draw_seed_packet
_entry_draw_seed_packet:
    jmp     _tramp_draw_seed_packet
    .align  8, 0x90

.globl _entry_fps_pace
_entry_fps_pace:
    jmp     _tramp_fps_pace
    .align  8, 0x90

.globl _entry_fps_gate
_entry_fps_gate:
    jmp     _tramp_fps_gate
    .align  8, 0x90

.globl _entry_pool_draw
_entry_pool_draw:
    jmp     _tramp_pool_draw
    .align  8, 0x90

.globl _entry_board_draw
_entry_board_draw:
    jmp     _tramp_board_draw
    .align  8, 0x90

.globl _entry_sc_loop2_cull
_entry_sc_loop2_cull:
    jmp     _tramp_sc_loop2_cull
    .align  8, 0x90

.globl _entry_draw_triangles_tex
_entry_draw_triangles_tex:
    jmp     _tramp_draw_triangles_tex
    .align  8, 0x90

.globl _entry_has_seed_type
_entry_has_seed_type:
    jmp     _tramp_has_seed_type
    .align  8, 0x90

.text

/* __thiscall(ecx=Graphics*, stack: [esp+4]=img, [esp+8]=x, [esp+12]=y) -> ret 0xc */
_tramp_glyph_atlas_draw:
    push    DWORD PTR [esp + 12]    /* y */
    push    DWORD PTR [esp + 12]    /* x (shifted by 4) */
    push    DWORD PTR [esp + 12]    /* img (shifted by 8) */
    push    ecx                     /* g */
    call    _c_glyph_atlas_draw
    add     esp, 16
    ret     12

/* __usercall(eax=D3DInterface*, [esp+4]=drawMode) -> ret 4 */
_tramp_setup_draw_mode:
    push    DWORD PTR [esp + 4]     /* drawMode */
    push    eax                     /* D3DInterface* */
    call    _c_setup_draw_mode
    add     esp, 8
    ret     4

/* Hooked at 0x005661b0 (SetLinearFilter: esi=IDirect3DDevice7*, bl=bool linear)
 * Locks bilinear filter permanently ON (1) to eliminate 150-250+ Blt<->BltTransformed
 * batch flushes and 3x SetTextureStageState calls per frame (1:1 Blt quads use -0.5
 * texel-center alignment + 1px replicated atlas clamp borders -> pixel-identical!). */
_tramp_set_linfilt:
    cmp     BYTE PTR [0x006a9f51], 1
    je      .Lslf_done
    push    ebx
    mov     bl, 1
    call    .Lslf_run_orig
    pop     ebx
.Lslf_done:
    ret
.Lslf_run_orig:
    push    ecx
    cmp     BYTE PTR [0x006a9f51], bl
    push    0x005661b7
    ret

/* Hooked at 0x005661bb (replaces: xor eax,eax; test bl,bl; setne al) */
_tramp_flush_linfilt:
    push    ecx
    push    edx
    call    _c_flush_quads
    pop     edx
    pop     ecx
    xor     eax, eax
    test    bl, bl
    setne   al
    ret

/* Hooked at 0x0046a606 (replaces: mov eax, [esi+0x20]; mov edx, [eax]) */
_tramp_flush_drawpool:
    push    ecx
    call    _c_drawpool_pre
    pop     ecx
    mov     eax, DWORD PTR [esi + 0x20]
    mov     edx, DWORD PTR [eax]
    ret

/* Hooked at 0x00568ec0 (D3DInterface::Flush, esi = D3DInterface*) */
_tramp_d3d_flush:
    cmp     BYTE PTR [esi + 0x3c], 0
    je      .Ldf_ret
    push    ecx
    push    edx
    call    _c_d3d_endscene_pre
    pop     edx
    pop     ecx
    mov     eax, 0x00568ec6
    jmp     eax
.Ldf_ret:
    ret

/* Hooked at 0x00565a10 (TextureData::ReleaseTextures, eax = TextureData*) */
_tramp_release_textures:
    push    eax
    push    ecx
    push    edx
    call    _c_release_textures_pre
    pop     edx
    pop     ecx
    pop     eax
    push    ebx
    push    esi
    push    edi
    mov     edi, eax
    mov     eax, 0x00565a15
    jmp     eax

/* Hooked at 0x005681f0 (D3DInterface::Blt: eax=img, edi=this, [esp+0x0c]=srcRect)
 * Replaces 6 bytes: cmp dword ptr [edi+0x54], 0; push ebx; push ebp
 * Preserves ZF from cmp for 0x005681fd jz! */
_tramp_d3d_blt:
    push    ecx
    push    edx
    lea     edx, [esp + 0x14]       /* &([orig_esp + 0x0c] = theSrcRect slot) */
    push    OFFSET _g_tmp_blt_rect
    push    edx
    push    eax
    call    _c_sprite_atlas_remap
    add     esp, 12
    pop     edx
    pop     ecx
    cmp     DWORD PTR [edi + 0x54], 0
    push    ebx
    push    ebp
    push    0x005681f6
    ret

/* Hooked at 0x00568520 (D3DInterface::BltTransformed: eax=img, [esp+0x14]=srcRect)
 * Replaces 6 bytes: push ebp; mov ebp, esp; and esp, -8 */
_tramp_d3d_blt_xform:
    push    ecx
    push    edx
    lea     edx, [esp + 0x1c]       /* &([orig_esp + 0x14] = theSrcRect slot) */
    push    OFFSET _g_tmp_xform_rect
    push    edx
    push    eax
    call    _c_sprite_atlas_remap
    add     esp, 12
    pop     edx
    pop     ecx
    push    ebp
    mov     ebp, esp
    and     esp, -8
    push    0x00568526
    ret

/* Hooked at 0x00590430 (MemoryImage::~MemoryImage: ecx = this)
 * Replaces 7 bytes: push -1; push 0x00648c78 */
_tramp_memimg_dtor:
    push    eax
    push    ecx
    push    edx
    push    ecx
    call    _c_on_memimg_destroy
    add     esp, 4
    pop     edx
    pop     ecx
    pop     eax
    push    -1
    push    0x00648c78
    push    0x00590437
    ret

/* =====================================================================
 * Safe __cdecl helpers for PopCap custom calling conventions
 * ===================================================================== */

/* void asm_call_d3d_check_error(int32_t hr, const char *msg) */
.globl _asm_call_d3d_check_error
_asm_call_d3d_check_error:
    push    edi
    mov     edi, DWORD PTR [esp + 12]   /* msg */
    push    DWORD PTR [esp + 8]         /* hr */
    mov     eax, 0x005644e0
    call    eax
    add     esp, 4
    pop     edi
    ret

/* void asm_call_orig_draw_image(void *g, void *img, int x, int y) */
/* Target 0x00587150: eax=g, ebx=img, [esp+4]=x, [esp+8]=y, ret 8 */
.globl _asm_call_orig_draw_image
_asm_call_orig_draw_image:
    push    ebx
    mov     eax, DWORD PTR [esp + 8]    /* g */
    mov     ebx, DWORD PTR [esp + 12]   /* img */
    push    DWORD PTR [esp + 20]        /* y */
    push    DWORD PTR [esp + 20]        /* x (shifted by 4) */
    mov     edx, 0x00587150
    call    edx
    pop     ebx
    ret

/* void asm_call_draw_image_rect(void *g, void *img, int x, int y, const SexyRect *r) */
/* Target 0x00587270: ecx=g, eax=&srcRect, stack(img, x, y), ret 12 */
.globl _asm_call_draw_image_rect
_asm_call_draw_image_rect:
    mov     ecx, DWORD PTR [esp + 4]    /* g */
    mov     eax, DWORD PTR [esp + 20]   /* r */
    push    DWORD PTR [esp + 16]        /* y */
    push    DWORD PTR [esp + 16]        /* x (shifted by 4) */
    push    DWORD PTR [esp + 16]        /* img (shifted by 8) */
    mov     edx, 0x00587270
    call    edx
    ret

/* =====================================================================
 * Zero-SEH fast paths for CreateImageTexture (0x567cf0) & D3DCheckError (0x5644e0)
 * ===================================================================== */

_tramp_create_image_tex:
    mov     edx, DWORD PTR [esp + 8]
    test    edx, edx
    je      .Lcit_slow
    mov     eax, DWORD PTR [edx + 0x40] /* TextureData* td */
    test    eax, eax
    je      .Lcit_slow
    cmp     DWORD PTR [eax + 0x3c], 0   /* td->mD3DInterface != 0 */
    je      .Lcit_slow
    mov     ecx, DWORD PTR [edx + 0x24] /* img->mWidth */
    cmp     ecx, DWORD PTR [eax + 0x14] /* td->mWidth */
    jne     .Lcit_slow
    mov     ecx, DWORD PTR [edx + 0x28] /* img->mHeight */
    cmp     ecx, DWORD PTR [eax + 0x18] /* td->mHeight */
    jne     .Lcit_slow
    mov     ecx, DWORD PTR [edx + 0x3c] /* img->mBitsChangedCount */
    cmp     ecx, DWORD PTR [eax + 0x2c] /* td->mBitsChangedCount */
    jne     .Lcit_slow
    mov     ecx, DWORD PTR [edx + 0x44] /* img->mD3DFlags */
    cmp     ecx, DWORD PTR [eax + 0x40] /* td->mD3DFlags */
    jne     .Lcit_slow
    mov     eax, 1
    ret     8
.Lcit_slow:
    push    -1
    push    0x0064d883
    mov     eax, 0x00567cf7
    jmp     eax

_tramp_d3d_check_error:
    cmp     DWORD PTR [esp + 4], 0
    jl      .Ldce_slow
    xor     eax, eax
    ret
.Ldce_slow:
    push    -1
    push    0x0064a558
    mov     eax, 0x005644e7
    jmp     eax

/* =====================================================================
 * Relocation-safe gdi42.dll DrawString & StringWidth fast paths
 * ===================================================================== */

_tramp_gdi_draw_string:
    pop     eax                         /* runtime VA = gdi_base + 0x1f45 */
    sub     eax, 0x1f45                 /* eax = gdi_base */
    push    eax                         /* save gdi_base at [esp+4] after next push */
    push    ecx                         /* save font_this at [esp+0] */
    push    DWORD PTR [esp + 28]        /* color */
    push    DWORD PTR [esp + 28]        /* str */
    push    DWORD PTR [esp + 28]        /* y */
    push    DWORD PTR [esp + 28]        /* x */
    push    DWORD PTR [esp + 28]        /* g */
    push    ecx                         /* font_this */
    push    eax                         /* gdi_base */
    call    _c_gdi_draw_string
    add     esp, 28
    test    eax, eax
    je      .Lgds_fallback
    add     esp, 8
    ret     0x20
.Lgds_fallback:
    pop     ecx
    pop     eax
    add     eax, 0x2d26
    push    ebp
    mov     ebp, esp
    sub     esp, 0xc
    jmp     eax

_tramp_gdi_string_width:
    pop     eax                         /* runtime VA = gdi_base + 0x3776 */
    sub     eax, 0x3776                 /* eax = gdi_base */
    push    eax
    push    ecx
    push    DWORD PTR [esp + 12]        /* str */
    push    ecx                         /* font_this */
    push    eax                         /* gdi_base */
    call    _c_gdi_string_width
    add     esp, 12
    test    eax, eax
    js      .Lgsw_fallback
    add     esp, 8
    ret     4
.Lgsw_fallback:
    pop     ecx
    pop     eax
    add     eax, 0x2e96
    push    ebp
    mov     ebp, esp
    sub     esp, 0xc
    jmp     eax

/* =====================================================================
 * Safe __cdecl helpers for PopCap Graphics & gdi42 internal routines
 * ===================================================================== */

.globl _asm_call_gfx_push_state
_asm_call_gfx_push_state:
    push    DWORD PTR [esp + 4]
    mov     eax, 0x00586b40
    call    eax
    ret

.globl _asm_call_gfx_set_colorize
_asm_call_gfx_set_colorize:
    mov     eax, DWORD PTR [esp + 4]
    mov     cl, BYTE PTR [esp + 8]
    mov     edx, 0x00586d10
    call    edx
    ret

.globl _asm_call_gfx_set_color
_asm_call_gfx_set_color:
    mov     ecx, DWORD PTR [esp + 4]
    mov     eax, DWORD PTR [esp + 8]
    mov     edx, 0x00586cc0
    call    edx
    ret

.globl _asm_call_gfx_pop_state
_asm_call_gfx_pop_state:
    push    edi
    mov     edi, DWORD PTR [esp + 8]
    mov     eax, 0x00586bd0
    call    eax
    pop     edi
    ret

.globl _asm_call_get_font_id
_asm_call_get_font_id:
    mov     ecx, DWORD PTR [esp + 4]
    push    0
    push    0xff
    mov     eax, 0x0058dff0
    call    eax
    ret

.globl _asm_call_gdi_map_lookup
_asm_call_gdi_map_lookup:
    mov     eax, DWORD PTR [esp + 4]
    mov     ecx, DWORD PTR [esp + 8]
    push    DWORD PTR [esp + 12]
    call    eax
    ret

.globl _asm_call_gdi_render_glyph
_asm_call_gdi_render_glyph:
    mov     eax, DWORD PTR [esp + 4]
    mov     ecx, DWORD PTR [esp + 8]
    push    DWORD PTR [esp + 12]
    call    eax
    ret

/* =====================================================================
 * OPT 8: DrawSeedPacket (0x004876f0) Display-List Cache Trampoline
 *   Entry: ecx = grayness, [esp+4..+32] = 8 args, __cdecl (ret 0)
 * ===================================================================== */
_tramp_draw_seed_packet:
    lea     eax, [esp + 4]
    push    ecx
    push    eax
    call    _c_draw_seed_packet
    add     esp, 8
    ret

.globl _asm_call_orig_draw_seed_packet
_asm_call_orig_draw_seed_packet:
    mov     eax, DWORD PTR [esp + 4]    /* args8 */
    mov     ecx, DWORD PTR [esp + 8]    /* grayness */
    push    DWORD PTR [eax + 28]
    push    DWORD PTR [eax + 24]
    push    DWORD PTR [eax + 20]
    push    DWORD PTR [eax + 16]
    push    DWORD PTR [eax + 12]
    push    DWORD PTR [eax + 8]
    push    DWORD PTR [eax + 4]
    push    DWORD PTR [eax + 0]
    call    .Ldsp_orig_entry
    add     esp, 32
    ret
.Ldsp_orig_entry:
    push    -1
    push    0x0064e87f
    mov     eax, 0x004876f7
    jmp     eax

/* int32_t asm_call_get_current_plant_cost(void *board, int32_t seedType, int32_t imitaterType)
 * Target 0x0041dae0: edi=board, eax=seedType, edx=imitaterType -> eax=cost */
.globl _asm_call_get_current_plant_cost
_asm_call_get_current_plant_cost:
    push    ebx
    push    esi
    push    edi
    mov     edi, DWORD PTR [esp + 16]   /* board */
    mov     eax, DWORD PTR [esp + 20]   /* seedType */
    mov     edx, DWORD PTR [esp + 24]   /* imitaterType */
    mov     ecx, 0x0041dae0
    call    ecx
    pop     edi
    pop     esi
    pop     ebx
    ret

/* void asm_call_gfx_copy_ctor(void *dst_g, const void *src_g)
 * Target 0x005869b0: edi=dst_g, [esp+4]=src_g -> ret 4 */
.globl _asm_call_gfx_copy_ctor
_asm_call_gfx_copy_ctor:
    push    edi
    mov     edi, DWORD PTR [esp + 8]    /* dst_g */
    push    DWORD PTR [esp + 12]        /* src_g */
    mov     eax, 0x005869b0
    call    eax
    pop     edi
    ret

/* void asm_call_gfx_dtor(void *g)
 * Target 0x00586b10: ecx=g -> ret 0 */
.globl _asm_call_gfx_dtor
_asm_call_gfx_dtor:
    mov     ecx, DWORD PTR [esp + 4]    /* g */
    mov     eax, 0x00586b10
    call    eax
    ret

/* =====================================================================
 * OPT 9: Live 30 / 60 / 90 / 120 FPS Engine Pacer (ProcessSafe hooks)
 *   0x00551ac7 -> _tramp_fps_pace (forces aVSync=0 for instant Frame-1 lock, returns eax=target_fps -> 0x00551ad6)
 *   0x00551e18 -> _tramp_fps_gate (gates UpdateFrames at 120 FPS -> exact 100Hz logic)
 * ===================================================================== */
_tramp_fps_pace:
    mov     BYTE PTR [esp + 0x27], 0    /* ensure Frame 1 obeys 30/60/90/120 cap immediately */
    push    ecx
    push    edx
    call    _c_get_target_fps
    pop     edx
    pop     ecx
    mov     edx, 0x00551ad6
    jmp     edx

_tramp_fps_gate:
    cmp     DWORD PTR _g_target_fps, 100
    jbe     .Lfg_orig
    lea     eax, [esp + 0x30]
    push    ecx
    push    edx
    push    eax
    push    esi
    call    _c_fps_should_update_120
    add     esp, 8
    pop     edx
    pop     ecx
    test    eax, eax
    jnz     .Lfg_orig
    mov     eax, 0x00551f90
    jmp     eax
.Lfg_orig:
    mov     edx, DWORD PTR [esi]
    mov     eax, DWORD PTR [edx + 0x24]
    mov     ecx, esi
    call    eax
    mov     edx, 0x00551e21
    jmp     edx

/* =====================================================================
 * OPT 10: PoolEffect::PoolEffectDraw (0x00469de0) Occluded SeedChooser Cull
 *   __stdcall(this=[esp+4], g=[esp+8], isNight=[esp+12]) -> ret 12
 *   Replaces 6 bytes: push ebp; mov ebp, esp; and esp, -8
 * ===================================================================== */
_tramp_pool_draw:
    push    DWORD PTR [esp + 8]         /* Graphics *g */
    call    _c_pool_should_skip
    add     esp, 4
    test    eax, eax
    jnz     .Lpd_skip
    push    ebp
    mov     ebp, esp
    and     esp, -8
    mov     eax, 0x00469de6
    jmp     eax
.Lpd_skip:
    ret     12

/* =====================================================================
 * OPT 11: Board::Draw (0x00416880) Occluded Quad Cull + SeedChooser Loop-2 Early Cull
 *   Board::Draw __stdcall(board=[esp+4], g=[esp+8]) -> ret 8
 *   SeedChooser Loop 2 @ 0x004849e5 (7B: mov edx,[esp+0x14]; mov esi,[ebx+0x20])
 * ===================================================================== */
_tramp_board_draw:
    push    DWORD PTR [esp + 8]         /* g */
    push    DWORD PTR [esp + 8]         /* board (shifted by 4) */
    call    _c_board_draw_wrap
    add     esp, 8
    ret     8

.globl _asm_call_orig_board_draw
_asm_call_orig_board_draw:
    push    DWORD PTR [esp + 8]         /* g */
    push    DWORD PTR [esp + 8]         /* board */
    call    .Lbd_orig_entry
    ret
.Lbd_orig_entry:
    push    ebp
    mov     ebp, esp
    and     esp, -8
    mov     eax, 0x00416886
    jmp     eax

_tramp_sc_loop2_cull:
    push    ecx
    push    edx
    push    ebx                         /* ChosenSeed *seed */
    push    DWORD PTR [esp + 0x20]      /* SeedChooserScreen *sc = [orig_esp + 0x14] */
    call    _c_sc_loop2_skip
    add     esp, 8
    pop     edx
    pop     ecx
    test    eax, eax
    jnz     .Lscl2_skip
    mov     edx, DWORD PTR [esp + 0x14]
    mov     esi, DWORD PTR [ebx + 0x20]
    mov     eax, 0x004849ec
    jmp     eax
.Lscl2_skip:
    mov     eax, 0x00484ad8
    jmp     eax

/* =====================================================================
 * OPT 12: D3DInterface::DrawTrianglesTex (0x00568e30) Reanim Sprite Atlas + Batcher
 *   Entry: eax=const Color*, [esp+4..+36]=9 args, ret 0x24
 *   Replaces 6 bytes: push ebx; push ebp; mov ebp, [esp+0x0c]
 * ===================================================================== */
_tramp_draw_triangles_tex:
    push    eax                         /* save color* */
    lea     edx, [esp + 8]              /* &args9[0] = orig [esp+4] */
    push    edx
    push    eax
    call    _c_draw_triangles_tex
    add     esp, 8
    test    eax, eax
    jnz     .Ldtt_done
    pop     eax
    push    ebx
    push    ebp
    mov     ebp, DWORD PTR [esp + 0x0c]
    mov     edx, 0x00568e36
    jmp     edx
.Ldtt_done:
    add     esp, 4
    ret     0x24

/* uint32_t asm_call_create_image_tex(void *d3d, void *img)
 * Target 0x00567cf0: __stdcall(d3d, img) -> ret 8, returns al */
.globl _asm_call_create_image_tex
_asm_call_create_image_tex:
    push    DWORD PTR [esp + 8]         /* img */
    push    DWORD PTR [esp + 8]         /* d3d (shifted by 4) */
    mov     eax, 0x00567cf0
    call    eax
    movzx   eax, al
    ret

/* =====================================================================
 * OPT 13: HasSeedType (0x00930000) 1/Frame Recount Throttle + O(1) Cache
 *   Entry: edi=LawnApp*, ebx=seedType -> returns al (bool), ret 0
 *   Replaces 6 bytes @ 0x00930000: pushad (60); mov ebp, 0x800 (bd 00 08 00 00)
 *   Preserves ecx, edx, ebx, esi, edi, ebp for 100% caller safety.
 * ===================================================================== */
_tramp_has_seed_type:
    push    ecx
    push    edx
    push    ebx                         /* seed_type */
    push    edi                         /* app */
    call    _c_has_seed_type
    add     esp, 8
    pop     edx
    pop     ecx
    ret

/* uint32_t asm_call_has_seed_full(void *app, uint32_t seed_type) */
.globl _asm_call_has_seed_full
_asm_call_has_seed_full:
    push    ebx
    push    esi
    push    edi
    mov     edi, DWORD PTR [esp + 16]   /* app */
    mov     ebx, DWORD PTR [esp + 20]   /* seed_type */
    call    .Lhsf_orig
    movzx   eax, al
    pop     edi
    pop     esi
    pop     ebx
    ret
.Lhsf_orig:
    pushad
    mov     ebp, 0x00000800
    mov     eax, 0x00930006
    jmp     eax

/* uint32_t asm_call_has_seed_body(void *app, uint32_t seed_type)
 * Skips the 563-iter recount at 0x00930000..0x00930060; calls 0x00930061 directly. */
.globl _asm_call_has_seed_body
_asm_call_has_seed_body:
    push    ebx
    push    esi
    push    edi
    mov     edi, DWORD PTR [esp + 16]   /* app */
    mov     ebx, DWORD PTR [esp + 20]   /* seed_type */
    mov     eax, 0x00930061
    call    eax
    movzx   eax, al
    pop     edi
    pop     esi
    pop     ebx
    ret
