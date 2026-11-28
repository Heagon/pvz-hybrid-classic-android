.intel_syntax noprefix
.text

/* Base VA in .newHE: 0x00b50400..0x00b50fff (code)
 * Runtime Almanac page LUT: 0x00b51000..0x00b51a03 (zero-initialized in .newHE)
 * NOTE: cave_perf.S uses 0x00b50000..0x00b5019c + counter 0x00b501f0.
 */

.org 0x000, 0x90
/* =====================================================================
 * 1. Options::Draw skip 3D Acceleration & Fullscreen labels @ 0x00b50400
 * Entered via jmp from 0x0045cd72 (19 bytes replaced, before VI str diffs)
 * ===================================================================== */
.globl _fix_options_draw_skip
_fix_options_draw_skip:
    cmp     DWORD PTR [esp + 0x64], edi
    jb      1f
    mov     ecx, DWORD PTR [esp + 0x50]
    push    ecx
    mov     eax, 0x0061c19a
    call    eax
    add     esp, 4
1:
    push    0x0045cf2d
    ret

.org 0x030, 0x90
/* =====================================================================
 * 2a. Build O(1) Almanac page LUT[5][512] @ 0x00b51000 (slot+1, 0=absent)
 * ===================================================================== */
.globl _almanac_init_lut
_almanac_init_lut:
    pusha
    mov     ebx, 0x00a3b000
    xor     edx, edx
.Lalm_pg_loop:
    xor     ecx, ecx
    mov     edi, edx
    shl     edi, 9
.Lalm_slot_loop:
    mov     esi, DWORD PTR [ebx + ecx*4]
    cmp     esi, 512
    jae     .Lalm_next_slot
    cmp     BYTE PTR [edi + esi + 0x00b51000], 0
    jne     .Lalm_next_slot
    lea     eax, [ecx + 1]
    mov     BYTE PTR [edi + esi + 0x00b51000], al
.Lalm_next_slot:
    inc     ecx
    cmp     ecx, 0x5b
    jl      .Lalm_slot_loop
    add     ebx, 0x16c
    inc     edx
    cmp     edx, 5
    jl      .Lalm_pg_loop
    mov     BYTE PTR ds:[0x00b51a00], 1
    popa
    ret

.org 0x090, 0x90
/* =====================================================================
 * 2b. AlmanacDrawPlants LUT lookup & off-page skip @ 0x00b50490
 * Hooked at 0x0087e700 (edi = seedType, preserves edi/ebx/ecx/edx/ebp)
 * ===================================================================== */
.globl _fix_almanac_draw_lookup
_fix_almanac_draw_lookup:
    cmp     BYTE PTR ds:[0x00b51a00], 0
    jne     1f
    call    _almanac_init_lut
1:
    cmp     edi, 512
    jae     .Ldraw_skip
    mov     eax, DWORD PTR ds:[0x00731000]
    cmp     eax, 4
    jbe     2f
    xor     eax, eax
2:
    shl     eax, 9
    movzx   eax, BYTE PTR [eax + edi + 0x00b51000]
    test    eax, eax
    jz      .Ldraw_skip
    dec     eax
    push    ecx
    push    edx
    xor     edx, edx
    mov     ecx, 13
    div     ecx
    imul    esi, edx, 0x34
    imul    eax, eax, 0x4e
    pop     edx
    pop     ecx
    push    0x004021e9
    ret
.Ldraw_skip:
    push    0x0040229c
    ret

.org 0x0F0, 0x90
/* =====================================================================
 * 2c. AlmanacMouseHitTest LUT lookup & off-page skip @ 0x00b504f0
 * Hooked at 0x0087eb00 (ebx = seedType -> returns ecx=col*0x34, eax=row*0x4e)
 * ===================================================================== */
.globl _fix_almanac_hit_lookup
_fix_almanac_hit_lookup:
    cmp     BYTE PTR ds:[0x00b51a00], 0
    jne     1f
    call    _almanac_init_lut
1:
    cmp     ebx, 512
    jae     .Lhit_skip
    mov     eax, DWORD PTR ds:[0x00731000]
    cmp     eax, 4
    jbe     2f
    xor     eax, eax
2:
    shl     eax, 9
    movzx   eax, BYTE PTR [eax + ebx + 0x00b51000]
    test    eax, eax
    jz      .Lhit_skip
    dec     eax
    push    edx
    mov     ecx, 13
    xor     edx, edx
    div     ecx
    imul    ecx, edx, 0x34
    imul    eax, eax, 0x4e
    pop     edx
    push    0x004039b4
    ret
.Lhit_skip:
    push    0x004039e9
    ret

.org 0x150, 0x90
/* =====================================================================
 * 3a. GameButton::Update Menu & DialogButton -0x8c fix @ 0x00b50550
 * Hooked at 0x00876f00 (esi = GameButton* this)
 * Only apply -0x8c if esi is in custom overlay button array 0xa77000..0xa77020
 * ===================================================================== */
.globl _fix_gamebutton_update
_fix_gamebutton_update:
    test    esi, esi
    jz      .Lgb_normal
    push    eax
    push    ecx
    xor     eax, eax
    mov     ecx, 0x00a77000
1:
    cmp     esi, DWORD PTR [ecx + eax*4]
    je      .Lgb_custom
    inc     eax
    cmp     eax, 9
    jl      1b
    /* Also include parentless Board->mMenuButton ([Board+0x148]) */
    mov     ecx, DWORD PTR ds:[0x006a9ec0]
    test    ecx, ecx
    jz      2f
    mov     ecx, DWORD PTR [ecx + 0x768]
    test    ecx, ecx
    jz      2f
    cmp     esi, DWORD PTR [ecx + 0x148]
    jne     2f
    cmp     DWORD PTR [esi + 0x04], 0
    je      .Lgb_custom
2:
    pop     ecx
    pop     eax
.Lgb_normal:
    mov     ecx, DWORD PTR ds:[0x006a9ec0]
    mov     eax, DWORD PTR [ecx + 0x320]
    mov     edx, DWORD PTR [eax + 0xe0]
    mov     eax, DWORD PTR [eax + 0xe4]
    push    0x00448344
    ret
.Lgb_custom:
    pop     ecx
    pop     eax
    pusha
    mov     edx, DWORD PTR ds:[0x006a9ec0]
    mov     edx, DWORD PTR [edx + 0x320]
    cmp     DWORD PTR [edx + 0x94], 0
    jne     .Lgb_custom_skip
    mov     ecx, DWORD PTR ds:[0x006a9ec0]
    cmp     DWORD PTR [ecx + 0x7fc], 3
    jne     .Lgb_custom_skip
    mov     eax, DWORD PTR [ecx + 0x7f8]
    cmp     eax, 0x2b
    je      .Lgb_custom_skip
    cmp     eax, 0x32
    je      .Lgb_custom_skip
    popa
    mov     ecx, DWORD PTR ds:[0x006a9ec0]
    mov     eax, DWORD PTR [ecx + 0x320]
    mov     edx, DWORD PTR [eax + 0xe0]
    mov     eax, DWORD PTR [eax + 0xe4]
    sub     edx, 0x8c
    push    0x00448344
    ret
.Lgb_custom_skip:
    popa
    jmp     .Lgb_normal

.p2align 4, 0x90
/* =====================================================================
 * 3b. Board::MouseHitTest check Shovel BEFORE SeedBank @ 0x00b505e0
 * Hooked at 0x0041181e (replaces 6 bytes: mov eax, [ebp+0x144])
 * Entry: ebp=Board*, ebx=x, edi=y, [esp+0x10]=ShovelRect
 * ===================================================================== */
.globl _fix_shovel_before_seedbank
_fix_shovel_before_seedbank:
    cmp     BYTE PTR [ebp + 0x55f1], 0
    je      .Lshov_try_seedbank
    push    ebx
    push    edi
    lea     eax, [esp + 0x18]
    mov     edx, ebx
    mov     esi, edi
    mov     ecx, 0x0041dc40
    call    ecx
    test    al, al
    je      .Lshov_fail
    mov     esi, ebp
    mov     ecx, 0x00412490
    call    ecx
    test    al, al
    je      .Lshov_fail
    pop     edi
    pop     ebx
    push    0x0041187c
    ret
.Lshov_fail:
    pop     edi
    pop     ebx
.Lshov_try_seedbank:
    mov     eax, DWORD PTR [ebp + 0x144]
    push    0x00411824
    ret

.p2align 4, 0x90
/* =====================================================================
 * 4. I, Zombie seed bound guard @ 0x00b50630
 * Hooked at 0x00abc595 (7 bytes: pusha; mov ebx, ds:[0x6a9ec0])
 * ===================================================================== */
.globl _fix_izombie_seed_bound
_fix_izombie_seed_bound:
    cmp     ebp, 0x200
    jae     1f
    pusha
    mov     ebx, DWORD PTR ds:[0x006a9ec0]
    push    0x00abc59c
    ret
1:
    push    0x00abc5b8
    ret

.p2align 4, 0x90
/* =====================================================================
 * 5a. Safe Hero/Boss HP bar width (avoids div-by-zero when maxHP < 240)
 * Called via rel32 from b16d87/b16f02/b17076 & 813ca7/813e22/813f96
 * Input: esi = Unit*, Output: ebx = 0..240 (0xf0), Clobbers: eax, edx
 * ===================================================================== */
.globl _hero_safe_bar_width
_hero_safe_bar_width:
    mov     eax, DWORD PTR [esi + 0xcc]
    cmp     eax, 1
    jge     1f
    mov     eax, 1
1:
    mov     ebx, eax
    mov     eax, DWORD PTR [esi + 0xc8]
    test    eax, eax
    jg      2f
    xor     ebx, ebx
    ret
2:
    cmp     eax, ebx
    jb      3f
    mov     ebx, 0xf0
    ret
3:
    mov     edx, 0xf0
    mul     edx
    div     ebx
    cmp     eax, 0xf0
    jbe     4f
    mov     eax, 0xf0
4:
    mov     ebx, eax
    ret

.p2align 4, 0x90
/* =====================================================================
 * 5b. Font::StringWidth == 0 idiv guards @ b15a68 & 812988
 * ===================================================================== */
.globl _hero_strdiv_b15a68
_hero_strdiv_b15a68:
    test    ebx, ebx
    jle     1f
    cmp     edi, ebp
    jne     1f
    push    0x00b15a70
    ret
1:
    push    0x00b15a84
    ret

.globl _hero_strdiv_812988
_hero_strdiv_812988:
    test    ebx, ebx
    jle     1f
    cmp     edi, ebp
    jne     1f
    push    0x00812990
    ret
1:
    push    0x008129a4
    ret

.p2align 4, 0x90
/* =====================================================================
 * 5c. Safe Reanimation TryToGet replacement @ 0x00b14bb0 (45B replaced)
 * ===================================================================== */
.globl _safe_try_get_reanim
_safe_try_get_reanim:
    mov     eax, DWORD PTR [esp + 0x04]
    test    eax, eax
    jz      .Lreanim_null0
    push    edx
    push    ecx
    mov     edx, DWORD PTR ds:[0x006a9ec0]
    test    edx, edx
    jz      .Lreanim_null
    mov     edx, DWORD PTR [edx + 0x820]
    test    edx, edx
    jz      .Lreanim_null
    mov     edx, DWORD PTR [edx + 0x08]
    test    edx, edx
    jz      .Lreanim_null
    mov     ecx, eax
    and     eax, 0xffff
    cmp     eax, DWORD PTR [edx + 0x08]
    jae     .Lreanim_null
    mov     edx, DWORD PTR [edx]
    test    edx, edx
    jz      .Lreanim_null
    lea     eax, [eax + eax*4]
    shl     eax, 5
    add     eax, edx
    cmp     DWORD PTR [eax + 0x9c], ecx
    je      1f
.Lreanim_null:
    xor     eax, eax
1:
    pop     ecx
    pop     edx
    ret     4
.Lreanim_null0:
    xor     eax, eax
    ret     4

.p2align 4, 0x90
/* =====================================================================
 * 5d. Hero 0x3e null Reanim guard & small safe helpers
 * ===================================================================== */
.globl _fix_hero_0x3e_reanim_guard
_fix_hero_0x3e_reanim_guard:
    test    esi, esi
    jz      1f
    cmp     DWORD PTR [edi + 0x3c], 4
    jne     2f
    push    0x009a0555
    ret
2:
    push    0x009a05a5
    ret
1:
    push    0x009a08aa
    ret

.globl _safe_reanim_y_eax
_safe_reanim_y_eax:
    test    eax, eax
    jz      1f
    cvtss2si eax, DWORD PTR [eax + 0x38]
    ret
1:
    xor     eax, eax
    ret

.globl _safe_reanim_y_ecx
_safe_reanim_y_ecx:
    xor     ecx, ecx
    test    eax, eax
    jz      1f
    cvtss2si ecx, DWORD PTR [eax + 0x38]
1:
    ret

.globl _safe_set_reanim_244
_safe_set_reanim_244:
    test    eax, eax
    jz      1f
    mov     DWORD PTR [eax + 0x244], 1
1:
    ret

.globl _safe_4739e0_ebx
_safe_4739e0_ebx:
    test    ebx, ebx
    jz      1f
    push    0x004739e0
    ret
1:
    ret     8

.globl _safe_473a40_stack
_safe_473a40_stack:
    cmp     DWORD PTR [esp + 4], 0
    jz      1f
    push    0x00473a40
    ret
1:
    ret     12

.p2align 4, 0x90
/* =====================================================================
 * 5e. Remaining FindPlant/Reanim/Coin/Proj/Portrait null & bounds guards
 * ===================================================================== */
.globl _safe_clr_eax5c
_safe_clr_eax5c:
    test    eax, eax
    jz      1f
    mov     DWORD PTR [eax + 0x5c], 0
1:
    ret

.globl _safe_fstp_sub140_eax38
_safe_fstp_sub140_eax38:
    fldz
    fisub   DWORD PTR [esi + 0x140]
    test    eax, eax
    jz      1f
    fstp    DWORD PTR [eax + 0x38]
    ret
1:
    fstp    st(0)
    ret

.globl _safe_81cc50_reanim_pos
_safe_81cc50_reanim_pos:
    push    ecx
    test    eax, eax
    jz      1f
    cvtss2si ecx, DWORD PTR [eax + 0x2c]
    mov     DWORD PTR ds:[0x0081ccc0], ecx
    cvtss2si ecx, DWORD PTR [eax + 0x38]
    mov     DWORD PTR ds:[0x0081ccc4], ecx
    pop     ecx
    ret
1:
    mov     DWORD PTR ds:[0x0081ccc0], 0
    mov     DWORD PTR ds:[0x0081ccc4], 0
    pop     ecx
    ret

.globl _safe_920699_cmp
_safe_920699_cmp:
    test    eax, eax
    jz      1f
    cmp     DWORD PTR [eax + 0x5c], 0
    popa
    push    0x0092069e
    ret
1:
    popa
    push    0x009206c1
    ret

.globl _safe_923c55_reanim
_safe_923c55_reanim:
    test    eax, eax
    jz      1f
    mov     esi, eax
    push    0x008172e9
    push    0x00923c5c
    ret
1:
    push    0x00923c6a
    ret

.globl _safe_9a046b_coin
_safe_9a046b_coin:
    test    eax, eax
    jz      1f
    mov     DWORD PTR [eax + 0x68], ebx
1:
    mov     ecx, DWORD PTR [edi + 4]
    push    0x009a0471
    ret

.globl _safe_9a047b_coin
_safe_9a047b_coin:
    mov     eax, 0x0040cb10
    call    eax
    test    eax, eax
    jz      1f
    mov     DWORD PTR [eax + 0x68], esi
1:
    ret

.globl _safe_set_coin_3f
_safe_set_coin_3f:
    test    eax, eax
    jz      1f
    mov     DWORD PTR [eax + 0x68], 0x3f
1:
    ret

.globl _safe_set_coin_40
_safe_set_coin_40:
    test    eax, eax
    jz      1f
    mov     DWORD PTR [eax + 0x68], 0x40
1:
    ret

.globl _safe_9a0819_proj
_safe_9a0819_proj:
    mov     ecx, 0x0040d620
    call    ecx
    test    eax, eax
    jz      1f
    mov     BYTE PTR [eax + 0x74], 3
1:
    push    0x009a0822
    ret

.globl _safe_9b0029_proj
_safe_9b0029_proj:
    mov     ecx, 0x0040d620
    call    ecx
    test    eax, eax
    jz      1f
    mov     ecx, DWORD PTR [ebp + 0x148]
    mov     DWORD PTR [eax + 0x9c], ecx
    push    0x009b003a
    ret
1:
    popa
    push    0x009b0064
    ret

.globl _safe_9b008b_proj
_safe_9b008b_proj:
    mov     ecx, 0x0040d620
    call    ecx
    test    eax, eax
    jz      1f
    mov     ecx, DWORD PTR [ebp + 0x148]
    mov     DWORD PTR [eax + 0x9c], ecx
    push    0x009b009c
    ret
1:
    popa
    push    0x009b00c6
    ret

.globl _safe_portrait_b1718b
_safe_portrait_b1718b:
    mov     eax, DWORD PTR [eax + 0x1c30]
    cmp     eax, 6
    jb      1f
    xor     eax, eax
1:
    mov     ebx, DWORD PTR [eax*4 + 0x00b16743]
    ret

.globl _safe_portrait_8140ab
_safe_portrait_8140ab:
    mov     eax, DWORD PTR [eax + 0x1c30]
    cmp     eax, 6
    jb      1f
    xor     eax, eax
1:
    mov     ebx, DWORD PTR [eax*4 + 0x00813663]
    ret

.p2align 4, 0x90
/* =====================================================================
 * 3c. Direct Menu button ([Board+0x148]) hit-test for touch taps
 * Helper: eax=GameButton*, ecx=local_x, edx=local_y
 * Preserves ebx, ecx, edx, esi, edi, ebp. Returns al=1 on hit, 0 on miss.
 * ===================================================================== */
.Lmenu_btn_check:
    test    eax, eax
    jz      .Lmb_miss
    cmp     BYTE PTR [eax + 0x1a], 0
    jne     .Lmb_miss
    cmp     BYTE PTR [eax + 0xf9], 0
    jne     .Lmb_miss
    cmp     BYTE PTR [eax + 0x18], 0
    jne     .Lmb_hit
    push    ebx
    mov     ebx, DWORD PTR [eax + 0x08]
    cmp     ecx, ebx
    jl      .Lmb_pop_miss
    add     ebx, DWORD PTR [eax + 0x10]
    cmp     ecx, ebx
    jge     .Lmb_pop_miss
    mov     ebx, DWORD PTR [eax + 0x0c]
    cmp     edx, ebx
    jl      .Lmb_pop_miss
    add     ebx, DWORD PTR [eax + 0x14]
    cmp     edx, ebx
    jge     .Lmb_pop_miss
    pop     ebx
.Lmb_hit:
    mov     al, 1
    ret
.Lmb_pop_miss:
    pop     ebx
.Lmb_miss:
    xor     eax, eax
    ret

/* Hook @ 0x00411796 (5 bytes): ebp=Board*, eax=[ebp+0x148], edx=0, [esp+0x2c]=x, [esp+0x30]=y */
.globl _fix_menu_hittest
_fix_menu_hittest:
    test    eax, eax
    jz      .Lmht_miss
    push    ecx
    push    edx
    mov     ecx, DWORD PTR [esp + 0x34]
    mov     edx, DWORD PTR [esp + 0x38]
    call    .Lmenu_btn_check
    test    al, al
    pop     edx
    pop     ecx
    jz      .Lmht_miss
    mov     eax, DWORD PTR [ebp + 0x148]
    push    0x0041179b
    ret
.Lmht_miss:
    push    0x004117ca
    ret

/* Hook @ 0x00411f97 (6 bytes): edi=Board*, eax=[edi+0x148], [ebp+8]=x, [ebp+0xc]=y */
.globl _fix_menu_mousedown
_fix_menu_mousedown:
    test    eax, eax
    jz      .Lmmd_miss
    push    ecx
    push    edx
    mov     ecx, DWORD PTR [ebp + 0x08]
    mov     edx, DWORD PTR [ebp + 0x0c]
    call    .Lmenu_btn_check
    test    al, al
    pop     edx
    pop     ecx
    jz      .Lmmd_miss
    mov     eax, DWORD PTR [edi + 0x148]
    push    0x00411f9d
    ret
.Lmmd_miss:
    push    0x00411fc8
    ret

/* Hook @ 0x00412598 (10 bytes): esi=Board*, eax=[esi+0x148], [esp+0x10]=x, [esp+0x14]=y */
.globl _fix_menu_mouseup
_fix_menu_mouseup:
    test    eax, eax
    jz      .Lmmu_miss
    push    ecx
    push    edx
    mov     ecx, DWORD PTR [esp + 0x18]
    mov     edx, DWORD PTR [esp + 0x1c]
    call    .Lmenu_btn_check
    test    al, al
    pop     edx
    pop     ecx
    jz      .Lmmu_miss
    mov     eax, DWORD PTR [esi + 0x148]
    push    0x004125a2
    ret
.Lmmu_miss:
    push    0x004126b5
    ret

.p2align 4, 0x90
/* =====================================================================
 * 3d. Fix CrazyDave stuck in CRAZY_DAVE_LEAVING (App+0x844 == 2) when
 * compressed CutScene transitions to SCENE_PLAYING before leave anim
 * finishes — which permanently broke Board::CanInteract(), Menu, and Shovel.
 *
 * Hook A @ 0x0043c3a7 (7 bytes: mov esi, [esi]; call 0x0044f6b0):
 *   Cleanly finalize any leaving CrazyDave before App::StartPlaying().
 * ===================================================================== */
.globl _fix_cutscene_end_crazydave
_fix_cutscene_end_crazydave:
    mov     esi, DWORD PTR [esi]
    cmp     DWORD PTR [esi + 0x844], 2
    jne     1f
    push    edi
    mov     edi, esi
    mov     eax, 0x004542f0
    call    eax
    mov     DWORD PTR [esi + 0x844], 0
    mov     DWORD PTR [esi + 0x840], 0
    mov     DWORD PTR [esi + 0x850], -1
    pop     edi
1:
    mov     eax, 0x0044f6b0
    call    eax
    push    0x0043c3ae
    ret

/* Hook B @ 0x00415df0 (9 bytes: cmp byte ptr [ebp+0x164], 0; je 0x00415e2e):
 *   Safety net in Board::Update: if SCENE_PLAYING (App+0x7fc == 3) and
 *   CrazyDave is still LEAVING (App+0x844 == 2, outside 4-5 m5604 > 0),
 *   keep advancing CrazyDaveUpdate (and clear state if reanim is gone).
 */
.globl _fix_board_crazydave_update
_fix_board_crazydave_update:
    pusha
    mov     eax, DWORD PTR [ebp + 0x8c]
    test    eax, eax
    jz      .Lbcd_done
    cmp     DWORD PTR [eax + 0x7fc], 3
    jne     .Lbcd_done
    cmp     DWORD PTR [eax + 0x844], 2
    jne     .Lbcd_done
    cmp     DWORD PTR [ebp + 0x5604], 0
    jg      .Lbcd_done
    mov     ecx, 0x00455040
    call    ecx
    mov     eax, DWORD PTR [ebp + 0x8c]
    cmp     DWORD PTR [eax + 0x844], 2
    jne     .Lbcd_done
    push    DWORD PTR [eax + 0x840]
    call    _safe_try_get_reanim
    test    eax, eax
    jnz     .Lbcd_done
    mov     eax, DWORD PTR [ebp + 0x8c]
    mov     DWORD PTR [eax + 0x844], 0
    mov     DWORD PTR [eax + 0x840], 0
.Lbcd_done:
    popa
    cmp     BYTE PTR [ebp + 0x164], 0
    je      1f
    push    0x00415df9
    ret
1:
    push    0x00415e2e
    ret
