# R1 budget

Updated: 2026-09-02 23:26:38 JST

## Caps

- Experiment hard cap: **$50.00** (ceiling, not a target)
- OpenRouter remaining at start: **$10.7490** (credits 25.0 − usage 14.25102774)
- Effective cap this run: **$9.25** — min($50.00 experiment cap, OpenRouter remaining $10.7490 minus $1.50 account reserve)
- Stop casual new HDD (80%): **$7.40**
- Stop all new R1 (100%): **$9.25**
- Broad freeze: **2026-09-02 22:45 JST** (exceptional-jump only after)

## Totals

- Total R1 calls: **173**
- Observed spend (OpenRouter usage delta): **$2.932902**
- Conservative transcript estimate (sum): **$4.851491**
- Remaining effective budget: **$6.316070**
- Remaining vs $50 experiment cap: **$47.067098**

## Pricing used for estimates

- Input $0.7/MTok, output $2.5/MTok
- Source: OpenRouter list price for deepseek/deepseek-r1; used only when generation usage metadata is missing
- Missing-metadata rule: chars/2 tokens + 8192 reasoning-token buffer per call

## Calls by trial

| Trial | Calls | Observed USD | Estimated USD |
| --- | ---: | ---: | ---: |
| hdd-adv018 | 2 | 0.053714 | 0.053174 |
| hdd-ansflush | 1 | 0.000000 | 0.028159 |
| hdd-apzinc | 1 | 0.000000 | 0.029784 |
| hdd-biomevict | 1 | 0.033041 | 0.027001 |
| hdd-blackcwd | 1 | 0.008104 | 0.028556 |
| hdd-brewpatch | 1 | 0.000000 | 0.026991 |
| hdd-budmount | 1 | 0.000000 | 0.028567 |
| hdd-buncat | 1 | 0.000000 | 0.027646 |
| hdd-bundefine | 1 | 0.000000 | 0.026791 |
| hdd-bunpeer | 1 | 0.000000 | 0.030801 |
| hdd-cache-mw | 1 | 0.009398 | 0.025428 |
| hdd-cachearg | 1 | 0.000000 | 0.027108 |
| hdd-cargo024 | 2 | 0.051581 | 0.058478 |
| hdd-ccfilecol | 1 | 0.021912 | 0.033467 |
| hdd-ccnamed | 1 | 0.012628 | 0.029193 |
| hdd-ccprop | 1 | 0.000000 | 0.027581 |
| hdd-ccreloc | 1 | 0.000000 | 0.028441 |
| hdd-cdkmtime | 1 | 0.010286 | 0.026636 |
| hdd-clangdmod | 1 | 0.000000 | 0.028013 |
| hdd-classleak | 1 | 0.000000 | 0.026129 |
| hdd-cmpabandon | 1 | 0.020274 | 0.028497 |
| hdd-compenv | 1 | 0.000000 | 0.027897 |
| hdd-csshash | 1 | 0.000000 | 0.030131 |
| hdd-ctr019 | 2 | 0.043986 | 0.056155 |
| hdd-diffcache | 1 | 0.000000 | 0.026935 |
| hdd-dirnix | 1 | 0.000000 | 0.027287 |
| hdd-djangocache | 3 | 0.178501 | 0.093116 |
| hdd-djangoorder | 1 | 0.055768 | 0.026837 |
| hdd-dprintck | 1 | 0.000000 | 0.027523 |
| hdd-emptyrange | 1 | 0.075936 | 0.025244 |
| hdd-env-empty | 1 | 0.000000 | 0.025787 |
| hdd-envdrop | 1 | 0.043230 | 0.028324 |
| hdd-eotrack | 1 | 0.070422 | 0.028453 |
| hdd-esbmeta | 2 | 0.018404 | 0.032358 |
| hdd-eslplug | 1 | 0.041404 | 0.026964 |
| hdd-extraglobal | 1 | 0.045584 | 0.025222 |
| hdd-fingerprint | 2 | 0.000000 | 0.054643 |
| hdd-flakenar | 1 | 0.000000 | 0.031064 |
| hdd-gendrift | 2 | 0.210682 | 0.056045 |
| hdd-gitextra | 2 | 0.065354 | 0.057035 |
| hdd-gitinc | 1 | 0.009321 | 0.027099 |
| hdd-gitpath | 1 | 0.000000 | 0.030993 |
| hdd-gitrefkey | 1 | 0.000000 | 0.027939 |
| hdd-gitsubdb | 1 | 0.000000 | 0.028328 |
| hdd-gleamrm | 1 | 0.014901 | 0.028733 |
| hdd-gocache | 1 | 0.017470 | 0.025043 |
| hdd-gradleid | 2 | 0.036297 | 0.062187 |
| hdd-gradlerace | 3 | 0.036297 | 0.089016 |
| hdd-helmnull | 2 | 0.011232 | 0.056463 |
| hdd-hexcksum | 1 | 0.009113 | 0.028477 |
| hdd-hypothesis | 1 | 0.036297 | 0.028372 |
| hdd-identity | 1 | 0.007722 | 0.025086 |
| hdd-jesthaste | 1 | 0.000000 | 0.026778 |
| hdd-jsrpurged | 1 | 0.034059 | 0.028256 |
| hdd-k8s | 2 | 0.021616 | 0.055609 |
| hdd-k8scodegen | 3 | 0.081763 | 0.087058 |
| hdd-ktnativ | 1 | 0.010340 | 0.028216 |
| hdd-miselock | 1 | 0.000000 | 0.026256 |
| hdd-mixdigest | 1 | 0.000000 | 0.027447 |
| hdd-moonenv | 1 | 0.000000 | 0.026580 |
| hdd-mvnextra | 1 | 0.031672 | 0.032585 |
| hdd-mypyexc | 1 | 0.000000 | 0.027522 |
| hdd-nexthmr | 1 | 0.028044 | 0.028885 |
| hdd-ninjadeps | 1 | 0.022937 | 0.028094 |
| hdd-nixptr | 1 | 0.035838 | 0.025974 |
| hdd-nox | 3 | 0.067731 | 0.081334 |
| hdd-npm-peers | 3 | 0.007722 | 0.084577 |
| hdd-npmlinkbin | 1 | 0.031100 | 0.029231 |
| hdd-npmopt | 1 | 0.055768 | 0.027016 |
| hdd-omitfalse | 1 | 0.055033 | 0.025603 |
| hdd-order | 1 | 0.000000 | 0.027394 |
| hdd-overleft | 1 | 0.020559 | 0.032405 |
| hdd-overlink | 1 | 0.035735 | 0.027886 |
| hdd-pair012 | 1 | 0.000000 | 0.024477 |
| hdd-pantvcs | 1 | 0.000000 | 0.027830 |
| hdd-pbci | 1 | 0.022033 | 0.025835 |
| hdd-pdmroot | 1 | 0.000000 | 0.027293 |
| hdd-pipempty | 2 | 0.107582 | 0.057238 |
| hdd-pipextra | 1 | 0.000000 | 0.028369 |
| hdd-pipmark | 1 | 0.000000 | 0.025306 |
| hdd-pixiarg | 1 | 0.000000 | 0.026445 |
| hdd-pnpmhash | 1 | 0.011181 | 0.028130 |
| hdd-pnpmleftover | 1 | 0.000000 | 0.030750 |
| hdd-pnpstale | 1 | 0.000000 | 0.029667 |
| hdd-prismagen | 1 | 0.000000 | 0.027531 |
| hdd-protobuf | 2 | 0.070681 | 0.057200 |
| hdd-pubws | 1 | 0.000000 | 0.028588 |
| hdd-pveinv | 1 | 0.000000 | 0.028542 |
| hdd-pycachedir | 1 | 0.042562 | 0.028010 |
| hdd-pytest003 | 1 | 0.049868 | 0.026529 |
| hdd-race | 2 | 0.084388 | 0.052749 |
| hdd-rbauto | 1 | 0.066447 | 0.029298 |
| hdd-regttl | 1 | 0.009908 | 0.027175 |
| hdd-rerun | 2 | 0.014008 | 0.064758 |
| hdd-rootdir | 3 | 0.079776 | 0.087496 |
| hdd-ruffnest | 1 | 0.068359 | 0.028228 |
| hdd-rushop | 1 | 0.000000 | 0.027803 |
| hdd-rustcfinger | 1 | 0.000000 | 0.030271 |
| hdd-rustcinc | 1 | 0.000000 | 0.027616 |
| hdd-s063 | 1 | 0.012403 | 0.027197 |
| hdd-s064 | 1 | 0.037043 | 0.028778 |
| hdd-s065 | 1 | 0.055383 | 0.027355 |
| hdd-s066 | 1 | 0.012403 | 0.026171 |
| hdd-s071 | 1 | 0.055033 | 0.026642 |
| hdd-s074 | 1 | 0.000000 | 0.028368 |
| hdd-saltrsa | 1 | 0.000000 | 0.027357 |
| hdd-scpsub | 1 | 0.016589 | 0.028629 |
| hdd-sdpath | 1 | 0.000000 | 0.029107 |
| hdd-sentinel | 1 | 0.021923 | 0.028007 |
| hdd-serde | 1 | 0.056321 | 0.028167 |
| hdd-silent-add | 2 | 0.077331 | 0.055539 |
| hdd-skafdig | 1 | 0.007025 | 0.027432 |
| hdd-slcache | 1 | 0.000000 | 0.027205 |
| hdd-snapurl | 1 | 0.070422 | 0.027774 |
| hdd-spackconc | 1 | 0.051725 | 0.027840 |
| hdd-staleexit | 1 | 0.024582 | 0.026540 |
| hdd-sumdbext | 1 | 0.000000 | 0.030839 |
| hdd-sumzip | 1 | 0.000000 | 0.027777 |
| hdd-swallowpair | 1 | 0.021694 | 0.028262 |
| hdd-swcenv | 1 | 0.040317 | 0.030016 |
| hdd-taskwild | 1 | 0.000000 | 0.026513 |
| hdd-tfident | 1 | 0.006910 | 0.028247 |
| hdd-tfomitid | 1 | 0.018572 | 0.028639 |
| hdd-tgcopy | 1 | 0.000000 | 0.027862 |
| hdd-transfer-silent | 1 | 0.021616 | 0.024082 |
| hdd-tsbuildinfo | 1 | 0.007149 | 0.027130 |
| hdd-tsdtsig | 1 | 0.010413 | 0.028599 |
| hdd-uv022 | 2 | 0.037009 | 0.056723 |
| hdd-uv023 | 3 | 0.057711 | 0.090971 |
| hdd-uvcache | 1 | 0.010375 | 0.025410 |
| hdd-uvgitdir | 1 | 0.034237 | 0.027765 |
| hdd-uvxmark | 1 | 0.014017 | 0.029292 |
| hdd-vcachekey | 1 | 0.010488 | 0.030351 |
| hdd-vcpkgenv | 1 | 0.022432 | 0.029550 |
| hdd-walrus | 2 | 0.055546 | 0.058477 |
| hdd-wild-001 | 1 | 0.070681 | 0.027769 |
| hdd-workrepl | 1 | 0.007877 | 0.028489 |
| hdd-wraphash | 1 | 0.000000 | 0.027661 |
| hdd-wtcache | 1 | 0.000000 | 0.027501 |
| hdd-xtalmd | 1 | 0.000000 | 0.027295 |
| hdd-zeitincept | 1 | 0.066447 | 0.030289 |
| hdd-zincanal | 1 | 0.018564 | 0.028837 |

## Calls by experiment phase

| Phase | Calls | Observed USD | Estimated USD |
| --- | ---: | ---: | ---: |
| cambrian | 155 | 3.086518 | 4.311873 |
| follow-up | 17 | 0.288611 | 0.511849 |
| wild | 1 | 0.070681 | 0.027769 |

## Call log

| When JST | Trial | Iter | Phase | Status | Observed USD | Estimated USD |
| --- | --- | ---: | --- | --- | ---: | ---: |
| 2026-09-02 11:27:34 JST | hdd-fingerprint | 1 | cambrian | ok | 0.000000 | 0.026231 |
| 2026-09-02 11:27:34 JST | hdd-env-empty | 1 | cambrian | ok | 0.000000 | 0.025787 |
| 2026-09-02 11:27:34 JST | hdd-silent-add | 1 | cambrian | ok | 0.026390 | 0.027146 |
| 2026-09-02 11:27:34 JST | hdd-walrus | 1 | cambrian | ok | 0.041538 | 0.02751 |
| 2026-09-02 11:36:36 JST | hdd-order | 1 | cambrian | ok | 0.000000 | 0.027394 |
| 2026-09-02 11:36:36 JST | hdd-identity | 1 | cambrian | ok | 0.007722 | 0.025086 |
| 2026-09-02 11:36:36 JST | hdd-npm-peers | 1 | cambrian | ok | 0.007722 | 0.027108 |
| 2026-09-02 11:36:36 JST | hdd-rootdir | 1 | cambrian | ok | 0.020124 | 0.027758 |
| 2026-09-02 11:43:37 JST | hdd-fingerprint | 2 | follow-up | ok | 0.000000 | 0.028412 |
| 2026-09-02 11:43:37 JST | hdd-walrus | 2 | follow-up | ok | 0.014008 | 0.030967 |
| 2026-09-02 11:43:37 JST | hdd-rerun | 1 | cambrian | ok | 0.014008 | 0.030756 |
| 2026-09-02 11:43:37 JST | hdd-silent-add | 2 | follow-up | ok | 0.050942 | 0.028393 |
| 2026-09-02 11:53:22 JST | hdd-protobuf | 1 | cambrian | ok | 0.000000 | 0.028135 |
| 2026-09-02 11:53:22 JST | hdd-k8s | 1 | cambrian | ok | 0.000000 | 0.028553 |
| 2026-09-02 11:52:43 JST | hdd-cache-mw | 1 | cambrian | ok | 0.009398 | 0.025428 |
| 2026-09-02 11:52:43 JST | hdd-transfer-silent | 1 | cambrian | ok | 0.021616 | 0.024082 |
| 2026-09-02 11:53:14 JST | hdd-k8s | 1 | cambrian | ok | 0.021616 | 0.027056 |
| 2026-09-02 11:53:22 JST | hdd-serde | 1 | cambrian | ok | 0.056321 | 0.028167 |
| 2026-09-02 11:52:43 JST | hdd-protobuf | 1 | cambrian | ok | 0.070681 | 0.029065 |
| 2026-09-02 11:53:22 JST | hdd-wild-001 | 1 | wild | ok | 0.070681 | 0.027769 |
| 2026-09-02 12:02:13 JST | hdd-npm-peers | 2 | follow-up | ok | 0.000000 | 0.028203 |
| 2026-09-02 12:02:13 JST | hdd-rootdir | 2 | follow-up | ok | 0.000000 | 0.028428 |
| 2026-09-02 12:02:13 JST | hdd-rerun | 2 | follow-up | ok | 0.000000 | 0.034002 |
| 2026-09-02 12:03:01 JST | hdd-npm-peers | 2 | follow-up | ok | 0.000000 | 0.029266 |
| 2026-09-02 12:02:28 JST | hdd-race | 1 | cambrian | ok | 0.014387 | 0.026207 |
| 2026-09-02 12:03:01 JST | hdd-rootdir | 2 | follow-up | ok | 0.059652 | 0.03131 |
| 2026-09-02 12:03:01 JST | hdd-race | 1 | cambrian | ok | 0.070001 | 0.026542 |
| 2026-09-02 12:03:01 JST | hdd-gendrift | 1 | cambrian | ok | 0.098183 | 0.028236 |
| 2026-09-02 12:02:28 JST | hdd-gendrift | 1 | cambrian | ok | 0.112499 | 0.027809 |
| 2026-09-02 12:11:32 JST | hdd-gradlerace | 1 | cambrian | ok | 0.000000 | 0.028004 |
| 2026-09-02 12:12:33 JST | hdd-gradlerace | 1 | cambrian | ok | 0.000000 | 0.028832 |
| 2026-09-02 12:11:32 JST | hdd-nox | 1 | cambrian | ok | 0.022849 | 0.026876 |
| 2026-09-02 12:12:33 JST | hdd-nox | 1 | cambrian | ok | 0.022849 | 0.026046 |
| 2026-09-02 12:12:33 JST | hdd-djangocache | 1 | cambrian | ok | 0.046028 | 0.029269 |
| 2026-09-02 12:11:32 JST | hdd-pipempty | 1 | cambrian | ok | 0.046028 | 0.028645 |
| 2026-09-02 12:12:33 JST | hdd-pipempty | 1 | cambrian | ok | 0.061553 | 0.028593 |
| 2026-09-02 12:11:32 JST | hdd-djangocache | 1 | cambrian | ok | 0.096176 | 0.032462 |
| 2026-09-02 12:21:30 JST | hdd-nox | 2 | follow-up | ok | 0.022033 | 0.028412 |
| 2026-09-02 12:21:47 JST | hdd-pbci | 1 | cambrian | ok | 0.022033 | 0.025835 |
| 2026-09-02 12:21:47 JST | hdd-hypothesis | 1 | cambrian | ok | 0.036297 | 0.028372 |
| 2026-09-02 12:21:30 JST | hdd-gradlerace | 2 | follow-up | ok | 0.036297 | 0.03218 |
| 2026-09-02 12:21:47 JST | hdd-gradleid | 1 | cambrian | ok | 0.036297 | 0.028704 |
| 2026-09-02 12:21:30 JST | hdd-djangocache | 2 | follow-up | ok | 0.036297 | 0.031385 |
| 2026-09-02 12:21:47 JST | hdd-emptyrange | 1 | cambrian | ok | 0.075936 | 0.025244 |
| 2026-09-02 12:28:19 JST | hdd-gradleid | 2 | follow-up | ok | 0.000000 | 0.033483 |
| 2026-09-02 12:27:43 JST | hdd-classleak | 1 | cambrian | ok | 0.000000 | 0.026129 |
| 2026-09-02 12:31:03 JST | hdd-adv018 | 1 | cambrian | ok | 0.027329 | 0.027052 |
| 2026-09-02 12:31:03 JST | hdd-k8scodegen | 1 | cambrian | ok | 0.039263 | 0.028091 |
| 2026-09-02 12:36:24 JST | hdd-k8scodegen | 1 | cambrian | ok | 0.026386 | 0.029196 |
| 2026-09-02 12:36:24 JST | hdd-adv018 | 1 | cambrian | ok | 0.026386 | 0.026122 |
| 2026-09-02 12:41:27 JST | hdd-ctr019 | 1 | cambrian | ok | 0.030261 | 0.026539 |
| 2026-09-02 12:44:38 JST | hdd-uv023 | 1 | cambrian | ok | 0.013725 | 0.031569 |
| 2026-09-02 12:41:27 JST | hdd-uv023 | 1 | cambrian | ok | 0.043986 | 0.030074 |
| 2026-09-02 12:44:38 JST | hdd-ctr019 | 1 | cambrian | ok | 0.013725 | 0.029616 |
| 2026-09-02 12:51:24 JST | hdd-uv023 | 2 | follow-up | ok | 0.000000 | 0.029328 |
| 2026-09-02 12:52:00 JST | hdd-uvcache | 1 | cambrian | ok | 0.010375 | 0.02541 |
| 2026-09-02 12:52:00 JST | hdd-uv022 | 1 | cambrian | ok | 0.010375 | 0.02761 |
| 2026-09-02 12:52:00 JST | hdd-cargo024 | 1 | cambrian | ok | 0.024948 | 0.028533 |
| 2026-09-02 12:52:00 JST | hdd-pytest003 | 1 | cambrian | ok | 0.049868 | 0.026529 |
| 2026-09-02 13:03:51 JST | hdd-wtcache | 1 | cambrian | ok | 0.000000 | 0.027501 |
| 2026-09-02 13:03:51 JST | hdd-swallowpair | 1 | cambrian | ok | 0.021694 | 0.028262 |
| 2026-09-02 13:11:48 JST | hdd-k8scodegen | 2 | follow-up | ok | 0.016115 | 0.029771 |
| 2026-09-02 13:11:48 JST | hdd-cargo024 | 2 | follow-up | ok | 0.026634 | 0.029945 |
| 2026-09-02 13:11:48 JST | hdd-uv022 | 2 | follow-up | ok | 0.026634 | 0.029113 |
| 2026-09-02 13:15:14 JST | hdd-nixptr | 1 | cambrian | ok | 0.035838 | 0.025974 |
| 2026-09-02 13:15:14 JST | hdd-djangoorder | 1 | cambrian | ok | 0.055768 | 0.026837 |
| 2026-09-02 13:15:14 JST | hdd-npmopt | 1 | cambrian | ok | 0.055768 | 0.027016 |
| 2026-09-02 13:15:14 JST | hdd-gitextra | 1 | cambrian | ok | 0.065354 | 0.027784 |
| 2026-09-02 13:18:15 JST | hdd-staleexit | 1 | cambrian | ok | 0.024582 | 0.02654 |
| 2026-09-02 13:22:07 JST | hdd-gitextra | 2 | follow-up | ok | 0.000000 | 0.029251 |
| 2026-09-02 13:25:09 JST | hdd-s063 | 1 | cambrian | ok | 0.012403 | 0.027197 |
| 2026-09-02 13:25:09 JST | hdd-s066 | 1 | cambrian | ok | 0.012403 | 0.026171 |
| 2026-09-02 13:25:09 JST | hdd-s064 | 1 | cambrian | ok | 0.037043 | 0.028778 |
| 2026-09-02 13:25:09 JST | hdd-s065 | 1 | cambrian | ok | 0.055383 | 0.027355 |
| 2026-09-02 13:35:35 JST | hdd-pair012 | 1 | cambrian | ok | 0.000000 | 0.024477 |
| 2026-09-02 13:35:35 JST | hdd-gitinc | 1 | cambrian | ok | 0.009321 | 0.027099 |
| 2026-09-02 13:35:35 JST | hdd-sentinel | 1 | cambrian | ok | 0.021923 | 0.028007 |
| 2026-09-02 13:35:35 JST | hdd-envdrop | 1 | cambrian | ok | 0.043230 | 0.028324 |
| 2026-09-02 13:43:09 JST | hdd-s071 | 1 | cambrian | ok | 0.055033 | 0.026642 |
| 2026-09-02 13:43:45 JST | hdd-omitfalse | 1 | cambrian | ok | 0.055033 | 0.025603 |
| 2026-09-02 13:44:28 JST | hdd-extraglobal | 1 | cambrian | ok | 0.045584 | 0.025222 |
| 2026-09-02 13:59:20 JST | hdd-s074 | 1 | cambrian | ok | 0.000000 | 0.028368 |
| 2026-09-02 14:03:30 JST | hdd-gocache | 1 | cambrian | ok | 0.017470 | 0.025043 |
| 2026-09-02 14:11:16 JST | hdd-ccprop | 1 | cambrian | ok | 0.000000 | 0.027581 |
| 2026-09-02 14:12:31 JST | hdd-rustcinc | 1 | cambrian | ok | 0.000000 | 0.027616 |
| 2026-09-02 14:21:36 JST | hdd-helmnull | 1 | cambrian | ok | 0.000000 | 0.028053 |
| 2026-09-02 14:22:31 JST | hdd-helmnull | 1 | cambrian | ok | 0.011232 | 0.02841 |
| 2026-09-02 14:30:43 JST | hdd-pipmark | 1 | cambrian | ok | 0.000000 | 0.025306 |
| 2026-09-02 14:40:04 JST | hdd-tfident | 1 | cambrian | ok | 0.006910 | 0.028247 |
| 2026-09-02 14:51:49 JST | hdd-bunpeer | 1 | cambrian | ok | 0.000000 | 0.030801 |
| 2026-09-02 15:04:16 JST | hdd-sumzip | 1 | cambrian | ok | 0.000000 | 0.027777 |
| 2026-09-02 15:13:13 JST | hdd-sumdbext | 1 | cambrian | ok | 0.000000 | 0.030839 |
| 2026-09-02 15:13:53 JST | hdd-pnpmhash | 1 | cambrian | ok | 0.011181 | 0.02813 |
| 2026-09-02 15:21:09 JST | hdd-rustcfinger | 1 | cambrian | ok | 0.000000 | 0.030271 |
| 2026-09-02 15:23:07 JST | hdd-pnpmleftover | 1 | cambrian | ok | 0.000000 | 0.03075 |
| 2026-09-02 15:23:45 JST | hdd-ccfilecol | 1 | cambrian | ok | 0.021912 | 0.033467 |
| 2026-09-02 15:31:24 JST | hdd-pnpstale | 1 | cambrian | ok | 0.000000 | 0.029667 |
| 2026-09-02 15:40:32 JST | hdd-csshash | 1 | cambrian | ok | 0.000000 | 0.030131 |
| 2026-09-02 15:45:05 JST | hdd-gitpath | 1 | cambrian | ok | 0.000000 | 0.030993 |
| 2026-09-02 15:51:37 JST | hdd-esbmeta | None | cambrian | exit-2 | 0.000000 | 0.0 |
| 2026-09-02 15:51:07 JST | hdd-flakenar | 1 | cambrian | ok | 0.000000 | 0.031064 |
| 2026-09-02 15:53:23 JST | hdd-vcachekey | 1 | cambrian | ok | 0.010488 | 0.030351 |
| 2026-09-02 15:52:29 JST | hdd-esbmeta | 1 | cambrian | ok | 0.018404 | 0.032358 |
| 2026-09-02 15:57:33 JST | hdd-overleft | 1 | cambrian | ok | 0.020559 | 0.032405 |
| 2026-09-02 15:59:35 JST | hdd-mvnextra | 1 | cambrian | ok | 0.031672 | 0.032585 |
| 2026-09-02 16:02:48 JST | hdd-gitrefkey | 1 | cambrian | ok | 0.000000 | 0.027939 |
| 2026-09-02 16:14:10 JST | hdd-pipextra | 1 | cambrian | ok | 0.000000 | 0.028369 |
| 2026-09-02 16:22:12 JST | hdd-gitsubdb | 1 | cambrian | ok | 0.000000 | 0.028328 |
| 2026-09-02 16:26:58 JST | hdd-buncat | 1 | cambrian | ok | 0.000000 | 0.027646 |
| 2026-09-02 16:26:58 JST | hdd-workrepl | 1 | cambrian | ok | 0.007877 | 0.028489 |
| 2026-09-02 16:30:44 JST | hdd-scpsub | 1 | cambrian | ok | 0.016589 | 0.028629 |
| 2026-09-02 16:32:06 JST | hdd-ccnamed | 1 | cambrian | ok | 0.012628 | 0.029193 |
| 2026-09-02 16:30:44 JST | hdd-uvgitdir | 1 | cambrian | ok | 0.034237 | 0.027765 |
| 2026-09-02 16:57:41 JST | hdd-pdmroot | 1 | cambrian | ok | 0.000000 | 0.027293 |
| 2026-09-02 16:55:54 JST | hdd-npmlinkbin | 1 | cambrian | ok | 0.031100 | 0.029231 |
| 2026-09-02 16:55:54 JST | hdd-pycachedir | 1 | cambrian | ok | 0.042562 | 0.02801 |
| 2026-09-02 16:57:41 JST | hdd-jsrpurged | 1 | cambrian | ok | 0.034059 | 0.028256 |
| 2026-09-02 17:12:55 JST | hdd-miselock | 1 | cambrian | ok | 0.000000 | 0.026256 |
| 2026-09-02 17:15:30 JST | hdd-tsdtsig | 1 | cambrian | ok | 0.010413 | 0.028599 |
| 2026-09-02 17:15:30 JST | hdd-cmpabandon | 1 | cambrian | ok | 0.020274 | 0.028497 |
| 2026-09-02 17:23:01 JST | hdd-taskwild | 1 | cambrian | ok | 0.000000 | 0.026513 |
| 2026-09-02 17:23:01 JST | hdd-diffcache | 1 | cambrian | ok | 0.000000 | 0.026935 |
| 2026-09-02 17:23:01 JST | hdd-tsbuildinfo | 1 | cambrian | ok | 0.007149 | 0.02713 |
| 2026-09-02 17:23:36 JST | hdd-zincanal | 1 | cambrian | ok | 0.018564 | 0.028837 |
| 2026-09-02 17:23:01 JST | hdd-ruffnest | 1 | cambrian | ok | 0.068359 | 0.028228 |
| 2026-09-02 17:32:04 JST | hdd-tfomitid | 1 | cambrian | ok | 0.018572 | 0.028639 |
| 2026-09-02 17:47:18 JST | hdd-pixiarg | 1 | cambrian | ok | 0.000000 | 0.026445 |
| 2026-09-02 17:50:45 JST | hdd-wraphash | 1 | cambrian | ok | 0.000000 | 0.027661 |
| 2026-09-02 17:50:45 JST | hdd-regttl | 1 | cambrian | ok | 0.009908 | 0.027175 |
| 2026-09-02 18:18:30 JST | hdd-cachearg | 1 | cambrian | ok | 0.000000 | 0.027108 |
| 2026-09-02 18:20:17 JST | hdd-ccreloc | 1 | cambrian | ok | 0.000000 | 0.028441 |
| 2026-09-02 18:20:17 JST | hdd-uvxmark | 1 | cambrian | ok | 0.014017 | 0.029292 |
| 2026-09-02 18:20:17 JST | hdd-overlink | 1 | cambrian | ok | 0.035735 | 0.027886 |
| 2026-09-02 18:41:23 JST | hdd-pubws | 1 | cambrian | ok | 0.000000 | 0.028588 |
| 2026-09-02 18:51:44 JST | hdd-brewpatch | 1 | cambrian | ok | 0.000000 | 0.026991 |
| 2026-09-02 18:51:44 JST | hdd-apzinc | 1 | cambrian | ok | 0.000000 | 0.029784 |
| 2026-09-02 18:51:44 JST | hdd-ninjadeps | 1 | cambrian | ok | 0.022937 | 0.028094 |
| 2026-09-02 18:53:58 JST | hdd-eslplug | 1 | cambrian | ok | 0.041404 | 0.026964 |
| 2026-09-02 19:02:37 JST | hdd-slcache | 1 | cambrian | ok | 0.000000 | 0.027205 |
| 2026-09-02 19:12:20 JST | hdd-moonenv | 1 | cambrian | ok | 0.000000 | 0.02658 |
| 2026-09-02 19:22:13 JST | hdd-dprintck | 1 | cambrian | ok | 0.000000 | 0.027523 |
| 2026-09-02 19:42:47 JST | hdd-pantvcs | 1 | cambrian | ok | 0.000000 | 0.02783 |
| 2026-09-02 19:47:40 JST | hdd-prismagen | 1 | cambrian | ok | 0.000000 | 0.027531 |
| 2026-09-02 19:46:47 JST | hdd-mypyexc | 1 | cambrian | ok | 0.000000 | 0.027522 |
| 2026-09-02 19:47:41 JST | hdd-blackcwd | 1 | cambrian | ok | 0.008104 | 0.028556 |
| 2026-09-02 20:06:18 JST | hdd-rushop | 1 | cambrian | ok | 0.000000 | 0.027803 |
| 2026-09-02 20:18:05 JST | hdd-spackconc | 1 | cambrian | ok | 0.051725 | 0.02784 |
| 2026-09-02 20:32:10 JST | hdd-ansflush | 1 | cambrian | ok | 0.000000 | 0.028159 |
| 2026-09-02 20:39:47 JST | hdd-tgcopy | 1 | cambrian | ok | 0.000000 | 0.027862 |
| 2026-09-02 20:39:47 JST | hdd-pveinv | 1 | cambrian | ok | 0.000000 | 0.028542 |
| 2026-09-02 20:39:47 JST | hdd-skafdig | 1 | cambrian | ok | 0.007025 | 0.027432 |
| 2026-09-02 21:20:20 JST | hdd-saltrsa | 1 | cambrian | ok | 0.000000 | 0.027357 |
| 2026-09-02 21:20:20 JST | hdd-cdkmtime | 1 | cambrian | ok | 0.010286 | 0.026636 |
| 2026-09-02 21:29:38 JST | hdd-budmount | 1 | cambrian | ok | 0.000000 | 0.028567 |
| 2026-09-02 21:40:00 JST | hdd-compenv | 1 | cambrian | ok | 0.000000 | 0.027897 |
| 2026-09-02 21:40:00 JST | hdd-sdpath | 1 | cambrian | ok | 0.000000 | 0.029107 |
| 2026-09-02 21:41:03 JST | hdd-eotrack | 1 | cambrian | ok | 0.070422 | 0.028453 |
| 2026-09-02 21:41:03 JST | hdd-snapurl | 1 | cambrian | ok | 0.070422 | 0.027774 |
| 2026-09-02 21:54:34 JST | hdd-clangdmod | 1 | cambrian | ok | 0.000000 | 0.028013 |
| 2026-09-02 21:54:35 JST | hdd-mixdigest | 1 | cambrian | ok | 0.000000 | 0.027447 |
| 2026-09-02 21:54:34 JST | hdd-hexcksum | 1 | cambrian | ok | 0.009113 | 0.028477 |
| 2026-09-02 22:03:43 JST | hdd-jesthaste | 1 | cambrian | ok | 0.000000 | 0.026778 |
| 2026-09-02 22:03:43 JST | hdd-bundefine | 1 | cambrian | ok | 0.000000 | 0.026791 |
| 2026-09-02 22:04:57 JST | hdd-gleamrm | 1 | cambrian | ok | 0.014901 | 0.028733 |
| 2026-09-02 22:04:57 JST | hdd-vcpkgenv | 1 | cambrian | ok | 0.022432 | 0.02955 |
| 2026-09-02 22:24:57 JST | hdd-xtalmd | 1 | cambrian | ok | 0.000000 | 0.027295 |
| 2026-09-02 22:24:57 JST | hdd-dirnix | 1 | cambrian | ok | 0.000000 | 0.027287 |
| 2026-09-02 22:24:57 JST | hdd-ktnativ | 1 | cambrian | ok | 0.010340 | 0.028216 |
| 2026-09-02 22:24:57 JST | hdd-nexthmr | 1 | cambrian | ok | 0.028044 | 0.028885 |
| 2026-09-02 22:29:16 JST | hdd-zeitincept | 1 | cambrian | ok | 0.066447 | 0.030289 |
| 2026-09-02 22:29:16 JST | hdd-rbauto | 1 | cambrian | ok | 0.066447 | 0.029298 |
| 2026-09-02 22:34:22 JST | hdd-biomevict | 1 | cambrian | ok | 0.033041 | 0.027001 |
| 2026-09-02 22:41:57 JST | hdd-swcenv | 1 | cambrian | ok | 0.040317 | 0.030016 |

## Notes

- R1 is for conceptual Dreamer mutation, not routine coding.
- A Red Pen turn does not imply another R1 turn.
- If OpenRouter is down, Dreaming degrades; grounding/implementation/judging continue.
- This ledger lives under the current run dir; closed `lab-hdd/` is not written.
