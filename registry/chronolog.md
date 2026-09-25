# Chronolog — Registro Cronografico Encadenado

> Generado automaticamente por `src/chronolog.py`. **NO editar a mano.**
> Cada entrada incluye el hash del evento y el hash del evento previo.
> Alterar cualquier linea invalida toda la cadena posterior.

- **Eventos:** 14
- **Generado:** 2026-09-24T17:24:17Z
- **Algoritmo:** SHA-256 sobre `(ts|tipo|entidad|desc|payload|prev_hash)`

---

## `2026-09-21T02:36:18Z` · **entidad_registrada** · `TEST-001`

Entidad TEST-001 registrada (categoria=test)

```json
{"estatus": "D", "origen": "observado", "provenance_hash": "fc9fdac9dbabce678fbc59998fed84eddc0b308f4489ad9ff6315be56aa1d520", "provenance_version": 1, "unidad": "Hz", "valor_principal": 100.0}
```

- `prev_hash` = `GENESIS`
- `hash`      = `f57309d6d2732dc7791ecacf3532a9bd878878f389a8bef4746805e008bb83d1`

---

## `2026-09-21T02:36:19Z` · **manifest** · `—`

Manifest v0.7.0 generado (chain_root=78e4154416af0b84...)

```json
{"chain_root": "78e4154416af0b8460a3b582c97470ff972f1def37c2114151ee3e2530d3d483", "file_count": 68, "manifest_sha256": "a0ecf88ad79585b048fe7a5ef78066960bc4a2164f0b7b7f5d9e749485f0231e", "version": "0.7.0"}
```

- `prev_hash` = `f57309d6d2732dc7791ecacf3532a9bd878878f389a8bef4746805e008bb83d1`
- `hash`      = `5d1efe91f069f8d7448d0d88caabcfc6f4b472efce65eff1b9f19ee436b350e5`

---

## `2026-09-21T03:25:22Z` · **manifest** · `—`

Manifest v0.7.0 generado (chain_root=9c01e16d3fae10f0...)

```json
{"chain_root": "9c01e16d3fae10f04327d3a169b919be1d94c3fbfd29d7ca44ab0a88ded32eb9", "file_count": 68, "manifest_sha256": "b7084f1ef9acef2bab504571f9b9c24d01e3ab4e7d1a6adec6cbf24cb6798b5b", "version": "0.7.0"}
```

- `prev_hash` = `5d1efe91f069f8d7448d0d88caabcfc6f4b472efce65eff1b9f19ee436b350e5`
- `hash`      = `237e3966cc413a5225d911e9878e464a586b5ef1d59f973af4b43b77d54cdd67`

---

## `2026-09-21T05:58:23Z` · **dataset_ingestado** · `COSM-007`

COSM-007 (Planck PR4 CamSpec TTTEEE likelihood runtime) ingestado

```json
{"bytes": 786538177.0, "dataset_path": "data\\extracted\\zen_runtime\\Planck_NPIPE_CamSpec_PR4_TTTEEE_likelihood_runtime\\CamSpec_PR4_TTTEEE_v1_20260919", "fuente": "PlanckPR4_CamSpec", "hash_raw": "014da657888ca32d90e432589bffc3e7f530a6d7a8d5eeefcb00fc6147cd8071", "n_files": 6, "provenance_hash": "1015874782a43e4a0728a84b21585cfe90eaefa007eec8f2742bcb572ac42f2e"}
```

- `prev_hash` = `237e3966cc413a5225d911e9878e464a586b5ef1d59f973af4b43b77d54cdd67`
- `hash`      = `51153b3f13d048df734a42eb1a54ae54a1fa6ae6f1c4e85727f90bd3bc88a407`

---

## `2026-09-21T05:58:23Z` · **dataset_ingestado** · `COSM-008`

COSM-008 (ACT DR6 TT/TE/EE multifrequency likelihood runtime) ingestado

```json
{"bytes": 496775545.0, "dataset_path": "data\\extracted\\zen_runtime\\ACT_DR6_full_multifrequency_TT_TE_EE_likelihood_ru\\ACT_DR6_TTTEEE_v1_20260917", "fuente": "ACTDR6_TTTEEE", "hash_raw": "904418cec753af4ecb197861f0eebbccfe41ca3bce6c68ea53b6e3e05a6eae6a", "n_files": 64, "provenance_hash": "795cfa7f84ebe9a01e663a978ca3903d58f2058a0c495e8feef07c30bd8ba1fa"}
```

- `prev_hash` = `51153b3f13d048df734a42eb1a54ae54a1fa6ae6f1c4e85727f90bd3bc88a407`
- `hash`      = `f723f61db04ae9e927ce5dcd341e4f8c8a8eeae7f6b027c2e41bdb05075261c9`

---

## `2026-09-21T05:58:24Z` · **dataset_ingestado** · `COSM-009`

COSM-009 (SPT-3G D1 T&E likelihood runtime) ingestado

```json
{"bytes": 62194455.0, "dataset_path": "data\\extracted\\zen_runtime\\SPT_3G_D1_T_E_likelihood_runtime_data_for_SPTLikel\\SPT3G_D1_TnE_v0_20260917", "fuente": "SPT3G_D1", "hash_raw": "2eeabff94fc43c3989bbd57a9328dd3ca097fec3e5123b579fec76dbd587ad6d", "n_files": 30, "provenance_hash": "b468099558b5d487089aa63050f288bd2000209f85514f66aee70f8d0d218e1e"}
```

- `prev_hash` = `f723f61db04ae9e927ce5dcd341e4f8c8a8eeae7f6b027c2e41bdb05075261c9`
- `hash`      = `adcdd9803e653ca2e983b25441c92149b620fe8fb1d3074ed6321cbd70fa30bd`

---

## `2026-09-21T05:58:24Z` · **dataset_ingestado** · `COSM-010`

COSM-010 (Joint Planck PR4 likelihood runtime) ingestado

```json
{"bytes": 97396129.0, "dataset_path": "data\\extracted\\zen_runtime\\Joint_Planck_PR4_likelihood_runtime_data_for_Joint\\JointCMB_planck_v1_20260919", "fuente": "JointCMB_planck", "hash_raw": "d1be35bb0d4caf4d52bacfe81a11cf47a0e9845741b4b675336563ec4191e15a", "n_files": 19, "provenance_hash": "44ef94991aad362ec3c65503286ca193a0af535be02dd6f9e2d53e3f9df67cc0"}
```

- `prev_hash` = `adcdd9803e653ca2e983b25441c92149b620fe8fb1d3074ed6321cbd70fa30bd`
- `hash`      = `7010fddeac33e11b14864f52a9e812fe2e0d8c566b7b4152a9ad1cf162b50e2b`

---

## `2026-09-21T05:58:25Z` · **dataset_ingestado** · `COSM-011`

COSM-011 (Joint ACT DR6 likelihood runtime) ingestado

```json
{"bytes": 142757457.0, "dataset_path": "data\\extracted\\zen_runtime\\Joint_ACT_DR6_likelihood_runtime_data_for_JointCMB\\JointCMB_act_v1_20260919", "fuente": "JointCMB_act", "hash_raw": "a7448bcd3051a5400b0dfe8c13308bc842ca923a317af41487f29d168449fd31", "n_files": 121, "provenance_hash": "2c23a9635368d690fc8b0790a7518063f69c3661d29ac94870714916b4633c3d"}
```

- `prev_hash` = `7010fddeac33e11b14864f52a9e812fe2e0d8c566b7b4152a9ad1cf162b50e2b`
- `hash`      = `a1153d86c4c5a04f23b829de7a7530b794731613fdfa9ebf777e6ad7f1acbfab`

---

## `2026-09-21T05:58:27Z` · **dataset_ingestado** · `COSM-012`

COSM-012 (Joint P4+ACT+SPT-3G fixtures) ingestado

```json
{"bytes": 97396129.0, "dataset_path": "data\\extracted\\zen_runtime\\Joint_Planck_PR4_likelihood_runtime_data_for_Joint", "fuente": "JointCMB_fixtures", "hash_raw": "d1be35bb0d4caf4d52bacfe81a11cf47a0e9845741b4b675336563ec4191e15a", "n_files": 19, "provenance_hash": "2406886a409f3cf90f7ec70b23fc1d2f4bb32f51af492be3de9dcbee40b9f907"}
```

- `prev_hash` = `a1153d86c4c5a04f23b829de7a7530b794731613fdfa9ebf777e6ad7f1acbfab`
- `hash`      = `0d991494ef2343827e3838e2351246f51e63ba6a88503a90459a9c43ea411d05`

---

## `2026-09-21T05:58:28Z` · **dataset_ingestado** · `COSM-013`

COSM-013 (CMB lensing likelihood ACT+SPT-3G+Planck) ingestado

```json
{"bytes": 3646471378.0, "dataset_path": "data\\extracted\\zen_runtime\\CMB_lensing_likelihood_data__ACT__SPT_3G__and_Plan\\act_planck_spt3g_lensing_data", "fuente": "Lensing_ACT_SPT_Planck", "hash_raw": "b09b7586736e4c886909c0534468db52887d39c33560f81e5a231c7c6ddf1f55", "n_files": 38, "provenance_hash": "32affaaa951fe695506d791bf4c7ca633ccbc90172a992b011fb1d4fb80c8bd7"}
```

- `prev_hash` = `0d991494ef2343827e3838e2351246f51e63ba6a88503a90459a9c43ea411d05`
- `hash`      = `5c679f77b2b3dd6938704c1a121af29dab2918616de692bc651fd437fe691b55`

---

## `2026-09-21T05:58:32Z` · **dataset_ingestado** · `COSM-014`

COSM-014 (CMB Lite CamSpec NPIPE likelihood) ingestado

```json
{"bytes": 348272595.0, "dataset_path": "data\\extracted\\zen_runtime\\CMB_Lite_Likelihood_Data\\cmblite_data", "fuente": "CMB_Lite_CamSpec", "hash_raw": "71d298ad2e4a2118936dd0234b0aac7de936460fca44903c30786d614535cfb1", "n_files": 68, "provenance_hash": "5cad6cbcb95fbacfceccaca84a43bdccbd91b1950e39f60b47889bb48f6cd7cb"}
```

- `prev_hash` = `5c679f77b2b3dd6938704c1a121af29dab2918616de692bc651fd437fe691b55`
- `hash`      = `4497a3613377465efcbe48b88a664b67200ded25b413c10c04d1dcb30b94f46a`

---

## `2026-09-21T05:58:34Z` · **dataset_ingestado** · `COSM-015`

COSM-015 (Joint foreground templates for JointCMBLikelihoods) ingestado

```json
{"bytes": 857789.0, "dataset_path": "data\\extracted\\zen_runtime\\Joint_foreground_templates_for_JointCMBLikelihoods\\JointCMB_fg_templates_v1_20260919", "fuente": "JointCMB_fg", "hash_raw": "509bf0f495b4f79242507da4a950b8aef88839f838b7228e071c03614d629a7e", "n_files": 10, "provenance_hash": "8ed4a19650f3d6ac1d6da546ad8aece12f1e024f7e4cc5ab12cd59ed02591387"}
```

- `prev_hash` = `4497a3613377465efcbe48b88a664b67200ded25b413c10c04d1dcb30b94f46a`
- `hash`      = `3583143247ff7e954c21ee2b2e4a233299fec724df4d90b7258511b289ff7ea1`

---

## `2026-09-21T05:58:35Z` · **dataset_ingestado** · `COSM-016`

COSM-016 (unimpeded chains (prediccion w(z) dinamico P1)) ingestado

```json
{"bytes": 95365414.0, "dataset_path": "data\\extracted\\pred_unimpeded\\handley-lab_unimpeded-v1.2.8", "fuente": "Handley_unimpeded", "hash_raw": "e028e5cc02626dc30ad8ef72c137264411797fff4905eeb9bb72c18b0ed38495", "n_files": 94, "provenance_hash": "0477ea29ffcb0a1a9f8797eaa925b7d6f4e2f7bf455e6080334a994ebff7b5d4"}
```

- `prev_hash` = `3583143247ff7e954c21ee2b2e4a233299fec724df4d90b7258511b289ff7ea1`
- `hash`      = `5842e0d356359f726973346f6a0da8fd37fd56afab19c04d263d77ff3b84bc63`

---

## `2026-09-24T17:24:05Z` · **manifest** · `—`

Manifest v0.7.0 generado (chain_root=572740023c9a5ff6...)

```json
{"chain_root": "572740023c9a5ff67c9feaacce8bcfce30e9a0128b3a51063f5df2064f630e96", "file_count": 2171, "manifest_sha256": "3eada6a7a025a80272f88c9a9b1f7dc83c58756f5b08d9236b15fa344beb9c12", "version": "0.7.0"}
```

- `prev_hash` = `5842e0d356359f726973346f6a0da8fd37fd56afab19c04d263d77ff3b84bc63`
- `hash`      = `2cb8b3112d31338dfffc4f2ae5a7ae915f8814ac42a67c41cca3f2efad2b8265`

---
