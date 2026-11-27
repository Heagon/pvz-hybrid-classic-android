.intel_syntax noprefix
.text

/* =====================================================================
 * Cave 1 @ VA 0x00b50000: TodParticleEmitter::UpdateSpawning throttle
 * Entered via jmp from 0x0051727c (replaces 10 bytes):
 *   33 ff 85 ed 89 7c 24 18 7e 27
 * Register state at 0x0051727c:
 *   ebx = TodParticleEmitter* this
 *   ebp = int spawnCount
 *   eax, ecx, edx = caller scratch (free to clobber)
 *   esp unchanged (must jump to 0x00517286 if ebp > 0, else 0x005172ad)
 * Note: local counter stored at [0x00b501f0] (RWX .newHE)
 * ===================================================================== */
.globl _particle_throttle_cave
_particle_throttle_cave:
    mov     eax, DWORD PTR [ebx + 0x04]
    test    eax, eax
    jz      .Lpt_done
    mov     ecx, DWORD PTR [eax + 0x08]
    test    ecx, ecx
    jz      .Lpt_done
    mov     edx, DWORD PTR [ecx + 0x48]    /* active particles */
    cmp     edx, 24
    jl      .Lpt_done
    /* tick counter at absolute 0x00b501f0 */
    mov     eax, 0x00b501f0
    mov     ecx, DWORD PTR [eax]
    inc     ecx
    mov     DWORD PTR [eax], ecx
    mov     eax, ebx
    shr     eax, 5
    add     ecx, eax
    cmp     edx, 60
    jl      .Lpt_med
    cmp     edx, 110
    jl      .Lpt_high

    /* Extreme load (>= 110 active particles): cap large bursts to 1, skip trails */
    cmp     ebp, 3
    jl      .Lpt_zero
    mov     ebp, 1
    jmp     .Lpt_done

.Lpt_high:
    /* High load (60..109 active): quarter bursts (min 1), 25% of single trails */
    cmp     ebp, 1
    jle     .Lpt_high_single
    add     ebp, 3
    sar     ebp, 2
    jmp     .Lpt_done
.Lpt_high_single:
    test    cl, 3
    jnz     .Lpt_zero
    jmp     .Lpt_done

.Lpt_med:
    /* Medium load (24..59 active): halve bursts & 50% of single trails */
    cmp     ebp, 1
    jle     .Lpt_med_single
    inc     ebp
    sar     ebp, 1
    jmp     .Lpt_done
.Lpt_med_single:
    test    cl, 1
    jz      .Lpt_done

.Lpt_zero:
    xor     ebp, ebp

.Lpt_done:
    xor     edi, edi
    mov     DWORD PTR [esp + 0x18], edi
    test    ebp, ebp
    jle     .Lpt_skip
    mov     eax, 0x00517286
    jmp     eax
.Lpt_skip:
    mov     eax, 0x005172ad
    jmp     eax

.org 0x90, 0x90
/* =====================================================================
 * Cave 2 @ VA 0x00b50090: Reanimation::MatrixFromTransform zero-angle fast path
 * Entered via jmp from 0x004720f0 (replaces 6 bytes):
 *   55 8b ec 83 e4 f8  (push ebp; mov ebp, esp; and esp, -8)
 * Register state at 0x004720f0:
 *   edi = ReanimatorTransform*
 *   esi = SexyMatrix3* out
 *   eax, ecx, edx = scratch (cdecl CRT calls clobber them in slow path)
 * ===================================================================== */
.globl _reanim_matrix_fast_cave
_reanim_matrix_fast_cave:
    mov     eax, DWORD PTR [edi + 0x08]
    or      eax, DWORD PTR [edi + 0x0c]
    and     eax, 0x7fffffff
    jnz     .Lrm_slow
    mov     eax, DWORD PTR [edi + 0x10]    /* mScaleX */
    mov     ecx, DWORD PTR [edi + 0x14]    /* mScaleY */
    xor     edx, edx
    mov     DWORD PTR [esi + 0x00], eax
    mov     DWORD PTR [esi + 0x04], edx
    mov     eax, DWORD PTR [edi + 0x00]    /* mTransX */
    mov     DWORD PTR [esi + 0x08], eax
    mov     DWORD PTR [esi + 0x0c], edx
    mov     DWORD PTR [esi + 0x10], ecx
    mov     ecx, DWORD PTR [edi + 0x04]    /* mTransY */
    mov     DWORD PTR [esi + 0x14], ecx
    mov     DWORD PTR [esi + 0x18], edx
    mov     DWORD PTR [esi + 0x1c], edx
    mov     DWORD PTR [esi + 0x20], 0x3f800000  /* 1.0f */
    ret
.Lrm_slow:
    push    ebp
    mov     ebp, esp
    and     esp, -8
    mov     eax, 0x004720f6
    jmp     eax

.org 0x100, 0x90
/* =====================================================================
 * Cave 3 @ VA 0x00b50100: CutScene SeedBank slide failsafe
 * Entered via jmp from 0x0043bafd (replaces 11 bytes):
 *   8b 4d 08 3b ce 7e 35 3b ca 7f 31
 * Register state at 0x0043bafd:
 *   ebp = CutScene*, edi = Board*, esi = slideStart, edx = slideEnd
 *   Only reached by game modes where SeedBank should be visible!
 * ===================================================================== */
.globl _seedbank_failsafe_cave
_seedbank_failsafe_cave:
    mov     ecx, DWORD PTR [ebp + 0x08]    /* mCutsceneTime */
    cmp     ecx, esi
    jle     .Lsb_skip
    cmp     ecx, edx
    jle     .Lsb_anim
    mov     eax, DWORD PTR [edi + 0x144]   /* Board::mSeedBank */
    test    eax, eax
    jz      .Lsb_skip
    cmp     DWORD PTR [eax + 0x0c], 0      /* SeedBank::mY < 0? */
    jge     .Lsb_skip
    mov     ecx, edx                       /* clamp t = slideEnd -> mY = 0 */
.Lsb_anim:
    mov     eax, 0x0043bb08
    jmp     eax
.Lsb_skip:
    mov     eax, 0x0043bb39
    jmp     eax

.org 0x140, 0x90
/* =====================================================================
 * Cave 4 @ VA 0x00b50140: SeedChooserScreen::Draw Loop 1 off-screen cull
 * Entered via jmp from 0x00484844 (replaces 9 bytes):
 *   83 fe 30 0f 84 90 00 00 00
 * Register/stack state at 0x00484844:
 *   esi = seedType, [esp+0x20] = card Y in widget coords
 * ===================================================================== */
.globl _seedchooser_cull1_cave
_seedchooser_cull1_cave:
    cmp     esi, 0x30
    je      .Lsc1_skip_ret
    mov     eax, DWORD PTR [esp + 0x20]
    cmp     eax, 40
    jl      .Lsc1_skip_ret
    cmp     eax, 560
    jg      .Lsc1_skip_ret
    push    0x0048484d
    ret
.Lsc1_skip_ret:
    push    0x004848dd
    ret

.org 0x170, 0x90
/* =====================================================================
 * Cave 5 @ VA 0x00b50170: SeedChooserScreen::Draw Loop 2 off-screen cull
 * Entered via jmp from 0x00484a98 (replaces 7 bytes):
 *   8b 43 20 6a 00 6a 01
 * Register/stack/FPU state at 0x00484a98:
 *   st(0) = 0.0f (fldz from 0xb0b9b6), edx = [ebx+0x34]
 *   [esp+0x18] = screen Y, [esp+0x20] = saved esi loop index
 * ===================================================================== */
.globl _seedchooser_cull2_cave
_seedchooser_cull2_cave:
    mov     eax, DWORD PTR [esp + 0x18]
    cmp     eax, -10
    jl      .Lsc2_skip
    cmp     eax, 560
    jg      .Lsc2_skip
    mov     eax, DWORD PTR [ebx + 0x20]
    push    0x0
    push    0x1
    push    0x00484a9f
    ret
.Lsc2_skip:
    fstp    st(0)
    mov     esi, DWORD PTR [esp + 0x20]
    push    0x00484ad8
    ret
