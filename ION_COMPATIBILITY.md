# Experimental ION compatibility

The 5.15 UAPI already contains modern ION allocation and heap-query structures. They match the donor's byte layouts and ioctl numbers on ARM32 and ARM64 (ion-uapi-results.json). Native headers remain unchanged.

ALIOTH_ION_COMPAT exposes /dev/ion and maps exactly heap ID 25 to qcom,system or qcom,system-uncached. The obsolete FREE ioctl returns ENOTTY, selecting the modern path in system/memory/libion/ion_legacy.c. Heap query advertises only system heap. Allocation errors and userspace copy failures release dma-buf/descriptor references. compat_ptr_ioctl handles fixed-width compat structures. Native qcom,dma-heaps DT registration creates the backing system heaps.

Unsupported heap masks, mixed masks, secure/content-protection flags, pool-force flags and nonzero unused fields return EOPNOTSUPP. No secure allocation is substituted with ordinary memory. Remaining donor heap IDs include CAMERA 20, ADSP 22, SYSTEM_SECURE 9, USER_CONTIG 26, QSEECOM 27, QSEECOM_TA 19, SPSS 13 and SECURE_DISPLAY 10. Qualcomm prefetch/drain/custom interfaces are also pending. libgsl/libcvp2/libcdsprpc import ion_alloc_fd; this bridge does not establish their complete allocation patterns or KGSL/DSP compatibility.

Compile and module link passed against the reference 5.15 exports, including modpost/LTO/BTF. No runtime ioctl/allocation test has been performed. The module is not installed. The candidate earlyboot fragment enables it for a future isolated image; production configs are unchanged. A full donor ION backport may still be necessary if the remaining ABI cannot be mapped faithfully.

## Nonsecure CMA extension

The bridge now includes donor heap IDs 22 (ADSP DMA) and 26 (user contiguous DMA), with cached/uncached native CMA providers. DT preserves sdsp_mem's 8 MiB and user_contig_mem's 16 MiB pools, their 4 MiB alignment and below-4-GiB allocation range. Heap queries copy at most the caller's requested count and only advertise backend pairs that are registered. The standalone extension passes LTO/modpost/BTF and checkpatch (0 errors/0 warnings). Candidate link and allocation/mapping on hardware remain unverified. All earlier statements of system-only implementation are superseded by this extension; unsupported secure/camera/QSEECOM requests remain explicitly rejected.


## QSEE communication pool extension

Donor kona-ion.dtsi defines IDs 27 (QSEECOM) and 19 (TA) as ordinary DMA heaps, distinct from secure/HYP heaps 9, 10, 13 and 14. Their reusable CMA pools are now translated with the donor sizes (20 MiB and 16 MiB), 4 MiB alignment and below-4-GiB allocation constraints. The bridge advertises each only after cached and uncached backends register. Secure flags remain unsupported and no protected heap is replaced. QSEE driver DT, secure-world shared-memory registration and runtime authentication remain separate validation requirements.

## SPSS/HLOS shared heap checkpoint

The latest source implements heap 13 using the donor 16 MiB reusable pool, 4 MiB alignment and below-4-GiB allocation range. Cached and uncached exporters use composite VMID 36 with RW permission; the optional HLOS flag adds VMID 3 with RW permission. Native mem-buf sharing preserves this ACL and permits composite HLOS CPU mapping only on alioth. Assignment failures propagate, and native ownership quarantine/reclaim remains in effect. Unsupported flag combinations remain rejected. Secure-display lending now uses the donor read-only permission.

The DT includes the required secure-buffer provider. SPSS firmware selection follows SoC 356 silicon revision: v1 uses spss1 names, v2/v2.1 use spss2 names; unknown revisions fail explicitly. Host fault, flag, permission, firmware-selection and compiled-DT checks pass. These checks do not prove real hypervisor assignment, SPSS service operation or Android boot. Heap 14 and camera heap 20 remain unsupported, and old-vendor encryption semantics require runtime verification. No device has been flashed or booted.
