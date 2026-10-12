from pathlib import Path
p=Path(__file__).resolve().parent;k=p/'msm-kernel'
f=k/'drivers/soc/qcom/spss_utils.c';s=f.read_text();s=s.replace('switch (cmd) {',"""switch (cmd) {
 case SPSS_IOC_SET_FW_CMAC: {
  const struct spss_ioc_set_fw_cmac *legacy = req;

  if (!kona_spss || size != sizeof(*legacy))
   return -EINVAL;
  if (!cmac_mem) {
   cmac_mem = ioremap(cmac_mem_addr, CMAC_MEM_SIZE);
   if (!cmac_mem)
    return -ENOMEM;
  }
  memset(saved_apps_cmac, 0, sizeof(saved_apps_cmac));
  memcpy(saved_fw_cmac, legacy->cmac, sizeof(saved_fw_cmac));
  memcpy(saved_apps_cmac, legacy->apps_cmac, sizeof(legacy->apps_cmac));
  ret = spss_set_saved_fw_cmac(saved_fw_cmac, sizeof(saved_fw_cmac));
  if (ret)
   return ret;
  ret = spss_set_saved_uefi_apps_cmac();
  if (ret)
   return ret;
  is_iar_active = true;
  spss_get_fw_calc_cmac();
  spss_get_apps_calc_cmac();
  break;
 }
""");f.write_text(s)
f=k/'drivers/remoteproc/qcom_spss.c';s=f.read_text();s=s.replace('glink->edge = qcom_glink_spss_register(glink->dev, glink->node);',"""if (glink->edge)
  return 0;
 glink->edge = qcom_glink_spss_register(glink->dev, glink->node);
 if (IS_ERR(glink->edge)) {
  int ret = PTR_ERR(glink->edge);

  glink->edge = NULL;
  return ret;
 }""")
s=s.replace('qcom_glink_spss_unregister(glink->edge);','if (glink->edge)\n  qcom_glink_spss_unregister(glink->edge);')
s=s.replace('rproc_remove_subdev(rproc, &glink->subdev);','glink_spss_subdev_stop(&glink->subdev, false);\n\trproc_remove_subdev(rproc, &glink->subdev);')
s=s.replace('ret = rproc_add(rproc);',"""/* Kona UEFI has already loaded SPSS. Match the donor transport lifetime
  * without guessing newer-SoC boot-state registers or reauthenticating it.
  */
 if (spss->kona) {
  ret = glink_spss_subdev_start(&spss->glink_subdev.subdev);
  if (ret)
   goto remove_subdev;
 }
	ret = rproc_add(rproc);""")
f.write_text(s)
