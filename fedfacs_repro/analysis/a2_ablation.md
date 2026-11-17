## cifar10
Controller (A2)    acc_best 72.13 ± 0.23 | acc_last10 70.17 ± 0.83 | jfi 0.997 | never 0.00 ± 0.00 | max_wait 11.00 ± 0.00 | pc_p10 63.25 ± 1.52
a=0.05             acc_best 71.33 ± 0.74 | acc_last10 70.04 ± 0.78 | jfi 0.999 | never 0.00 ± 0.00 | max_wait 10.00 ± 0.00 | pc_p10 63.21 ± 1.01
a=0.10             acc_best 72.01 ± 0.36 | acc_last10 70.46 ± 0.33 | jfi 0.998 | never 0.00 ± 0.00 | max_wait 10.00 ± 0.00 | pc_p10 60.54 ± 3.21
a=0.5              acc_best 70.88 ± 0.74 | acc_last10 68.81 ± 0.95 | jfi 0.916 | never 0.00 ± 0.00 | max_wait 15.67 ± 0.58 | pc_p10 57.27 ± 4.09
a=1 (no fairness)  acc_best 69.54 ± 0.35 | acc_last10 65.58 ± 0.72 | jfi 0.557 | never 10.00 ± 1.00 | max_wait 100.00 ± 0.00 | pc_p10 55.17 ± 1.28
  a=0.05 minus A2: acc_best -0.803[-1.910,-0.100] ; acc_last10 -0.123[-0.600,+0.267] ; jfi +0.001[+0.001,+0.002] ; max_wait -1.000[-1.000,-1.000]
  a=0.10 minus A2: acc_best -0.117[-0.310,+0.030] ; acc_last10 +0.296[-0.319,+1.239] ; jfi +0.001[+0.000,+0.001] ; max_wait -1.000[-1.000,-1.000]
  a=0.5 minus A2: acc_best -1.253[-1.900,-0.730] ; acc_last10 -1.360[-2.742,+0.077] ; jfi -0.081[-0.117,-0.057] ; max_wait +4.667[+4.000,+5.000]
  a=1 (no fairness) minus A2: acc_best -2.593[-2.770,-2.450] ; acc_last10 -4.586[-5.695,-3.328] ; jfi -0.440[-0.462,-0.415] ; max_wait +89.000[+89.000,+89.000]
  A2 minus a2_nopen (penalty helps if >0): acc_best +0.043[-0.120,+0.220] ; acc_last10 -0.216[-1.047,+0.468] ; jfi +0.000[-0.000,+0.000] | nopen means best 72.09 last10 70.38
## fmnist
Controller (A2)    acc_best 85.54 ± 0.34 | acc_last10 84.57 ± 0.55 | jfi 0.998 | never 0.00 ± 0.00 | max_wait 10.67 ± 0.58 | pc_p10 76.30 ± 2.18
a=0.05             acc_best 85.49 ± 0.47 | acc_last10 84.18 ± 0.66 | jfi 0.998 | never 0.00 ± 0.00 | max_wait 10.33 ± 0.58 | pc_p10 73.27 ± 1.74
a=0.10             acc_best 85.24 ± 0.39 | acc_last10 83.67 ± 0.42 | jfi 0.998 | never 0.00 ± 0.00 | max_wait 10.00 ± 0.00 | pc_p10 73.93 ± 3.96
a=0.5              acc_best 85.32 ± 0.33 | acc_last10 83.04 ± 1.13 | jfi 0.941 | never 0.00 ± 0.00 | max_wait 14.33 ± 0.58 | pc_p10 76.60 ± 1.99
a=1 (no fairness)  acc_best 83.36 ± 1.09 | acc_last10 79.00 ± 0.14 | jfi 0.346 | never 20.33 ± 1.53 | max_wait 100.00 ± 0.00 | pc_p10 68.19 ± 6.32
  a=0.05 minus A2: acc_best -0.057[-0.720,+0.780] ; acc_last10 -0.390[-0.774,+0.072] ; jfi +0.001[-0.001,+0.002] ; max_wait -0.333[-1.000,+0.000]
  a=0.10 minus A2: acc_best -0.303[-0.860,+0.520] ; acc_last10 -0.903[-1.327,-0.295] ; jfi +0.000[-0.001,+0.001] ; max_wait -0.667[-1.000,+0.000]
  a=0.5 minus A2: acc_best -0.220[-0.770,+0.500] ; acc_last10 -1.530[-3.424,-0.286] ; jfi -0.056[-0.060,-0.052] ; max_wait +3.667[+3.000,+4.000]
  a=1 (no fairness) minus A2: acc_best -2.187[-3.280,-0.570] ; acc_last10 -5.571[-6.344,-5.091] ; jfi -0.652[-0.664,-0.641] ; max_wait +89.333[+89.000,+90.000]
  A2 minus a2_nopen (penalty helps if >0): acc_best +0.137[-0.270,+0.350] ; acc_last10 +0.385[+0.140,+0.765] ; jfi +0.000[-0.000,+0.001] | nopen means best 85.41 last10 84.18
