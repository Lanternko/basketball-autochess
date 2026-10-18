# 階段 A：所有成對區間

差值一律左版本減右版本；RMSE、MAE較低好，r較高好，校準斜率需對1判讀。既有seed為第七批2000次；其餘5000次。主要判準為聯合區間。

## 2024-25，25場

| 比較 | 指標 | 差值 | 舊seed95% | 新seed95% | 球隊95% | 聯合95% |
|---|---|---:|---|---|---|---|
| v3-minus-v4 | netRMSE | 0.034 | -0.251, 0.320 | -0.257, 0.329 | -0.747, 0.781 | -0.852, 0.863 |
| v3-minus-v4 | netCorrelation | -0.123 | -0.155, -0.093 | -0.158, -0.090 | -0.225, -0.037 | -0.236, -0.029 |
| v3-minus-v4 | netSDRatio | -0.300 | -0.343, -0.256 | -0.341, -0.258 | -0.431, -0.140 | -0.448, -0.127 |
| v3-minus-v4 | calibrationSlope | 0.056 | 0.012, 0.100 | 0.010, 0.101 | -0.130, 0.227 | -0.138, 0.245 |
| v3-minus-v4 | winMAE | 0.397 | 0.190, 0.620 | 0.197, 0.623 | -0.603, 1.443 | -0.640, 1.550 |
| v3-minus-v4 | winRMSE | 0.768 | 0.458, 1.042 | 0.470, 1.067 | -0.131, 1.765 | -0.260, 1.915 |
| v3-minus-v4 | winSlope | 0.119 | 0.070, 0.165 | 0.070, 0.166 | 0.074, 0.167 | 0.037, 0.198 |
| v3-minus-v4 | calibrationError | -0.056 | -0.100, -0.012 | -0.101, -0.010 | -0.225, 0.130 | -0.238, 0.138 |
| v3-minus-v4 | defenseCorrelation | -0.005 | -0.074, 0.066 | -0.071, 0.067 | -0.088, 0.087 | -0.125, 0.123 |
| v3-minus-v4 | defenseSDRatio | 0.022 | -0.032, 0.070 | -0.033, 0.074 | -0.052, 0.102 | -0.085, 0.131 |
| v3-minus-v4 | residualSD | -0.678 | -0.934, -0.411 | -0.949, -0.401 | -0.951, -0.402 | -1.085, -0.249 |
| v3-minus-simple | netRMSE | 0.619 | — | 0.464, 0.800 | -0.890, 1.882 | -0.915, 1.914 |
| v3-minus-simple | netCorrelation | -0.146 | — | -0.171, -0.126 | -0.338, 0.055 | -0.339, 0.055 |
| v3-minus-simple | netSDRatio | -0.180 | — | -0.210, -0.144 | -0.334, -0.000 | -0.336, 0.013 |
| v3-minus-simple | calibrationSlope | -0.028 | — | -0.064, 0.006 | -0.282, 0.214 | -0.294, 0.214 |
| v3-minus-simple | winMAE | -0.077 | — | -0.267, 0.190 | -2.117, 1.885 | -2.031, 1.896 |
| v3-minus-simple | winRMSE | 0.194 | — | -0.064, 0.519 | -1.861, 2.273 | -1.850, 2.323 |
| v3-minus-simple | winSlope | -0.205 | — | -0.238, -0.173 | -0.274, -0.150 | -0.292, -0.135 |
| v3-minus-simple | calibrationError | 0.028 | — | -0.006, 0.064 | -0.211, 0.283 | -0.210, 0.294 |
| v3-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-shrink | netRMSE | 1.061 | — | 0.906, 1.242 | -0.338, 2.146 | -0.326, 2.167 |
| v3-minus-shrink | netCorrelation | -0.146 | — | -0.171, -0.126 | -0.338, 0.055 | -0.339, 0.055 |
| v3-minus-shrink | netSDRatio | 0.018 | — | -0.011, 0.054 | -0.124, 0.196 | -0.126, 0.217 |
| v3-minus-shrink | calibrationSlope | -0.174 | — | -0.210, -0.140 | -0.438, 0.084 | -0.444, 0.085 |
| v3-minus-shrink | winMAE | 0.305 | — | 0.115, 0.572 | -1.418, 1.939 | -1.371, 1.986 |
| v3-minus-shrink | winRMSE | 0.727 | — | 0.468, 1.051 | -1.090, 2.506 | -1.073, 2.515 |
| v3-minus-shrink | winSlope | -0.249 | — | -0.282, -0.216 | -0.310, -0.198 | -0.328, -0.181 |
| v3-minus-shrink | calibrationError | 0.174 | — | 0.140, 0.210 | -0.084, 0.431 | -0.084, 0.434 |
| v3-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-v1 | netRMSE | 0.020 | — | -0.250, 0.280 | -1.002, 0.948 | -1.145, 1.011 |
| v3-minus-v1 | netCorrelation | 0.060 | — | 0.014, 0.109 | -0.107, 0.231 | -0.116, 0.245 |
| v3-minus-v1 | netSDRatio | 0.195 | — | 0.138, 0.250 | 0.098, 0.301 | 0.078, 0.319 |
| v3-minus-v1 | calibrationSlope | -0.088 | — | -0.154, -0.013 | -0.282, 0.109 | -0.298, 0.141 |
| v3-minus-v1 | winMAE | -0.270 | — | -0.630, 0.057 | -1.258, 0.785 | -1.478, 0.833 |
| v3-minus-v1 | winRMSE | -0.064 | — | -0.505, 0.373 | -1.365, 1.191 | -1.583, 1.332 |
| v3-minus-v1 | winSlope | 0.033 | — | -0.023, 0.088 | -0.030, 0.094 | -0.065, 0.130 |
| v3-minus-v1 | calibrationError | 0.088 | — | 0.013, 0.155 | -0.122, 0.262 | -0.152, 0.279 |
| v3-minus-v1 | defenseCorrelation | 0.085 | — | 0.034, 0.163 | -0.253, 0.358 | -0.248, 0.402 |
| v3-minus-v1 | defenseSDRatio | 0.381 | — | 0.306, 0.440 | 0.156, 0.616 | 0.141, 0.626 |
| v3-minus-v1 | residualSD | -0.664 | — | -0.901, -0.434 | -0.874, -0.462 | -1.028, -0.315 |
| v3-minus-v3-signals-off | netRMSE | -0.035 | — | -0.308, 0.242 | -0.874, 0.767 | -1.001, 0.814 |
| v3-minus-v3-signals-off | netCorrelation | 0.069 | — | 0.024, 0.114 | -0.068, 0.207 | -0.077, 0.224 |
| v3-minus-v3-signals-off | netSDRatio | 0.189 | — | 0.155, 0.219 | 0.088, 0.292 | 0.079, 0.304 |
| v3-minus-v3-signals-off | calibrationSlope | -0.070 | — | -0.130, -0.001 | -0.249, 0.118 | -0.271, 0.144 |
| v3-minus-v3-signals-off | winMAE | -0.587 | — | -0.927, -0.203 | -1.472, 0.343 | -1.675, 0.470 |
| v3-minus-v3-signals-off | winRMSE | -0.318 | — | -0.763, 0.098 | -1.460, 0.789 | -1.640, 0.899 |
| v3-minus-v3-signals-off | winSlope | -0.017 | — | -0.060, 0.028 | -0.085, 0.045 | -0.115, 0.074 |
| v3-minus-v3-signals-off | calibrationError | 0.070 | — | 0.001, 0.130 | -0.135, 0.220 | -0.164, 0.235 |
| v3-minus-v3-signals-off | defenseCorrelation | 0.084 | — | 0.020, 0.162 | -0.257, 0.349 | -0.246, 0.389 |
| v3-minus-v3-signals-off | defenseSDRatio | 0.420 | — | 0.348, 0.473 | 0.194, 0.652 | 0.176, 0.665 |
| v3-minus-v3-signals-off | residualSD | 0.001 | — | -0.202, 0.197 | -0.208, 0.207 | -0.327, 0.330 |
| v4-minus-simple | netRMSE | 0.585 | 0.395, 0.814 | 0.396, 0.811 | -0.872, 1.779 | -0.838, 1.811 |
| v4-minus-simple | netCorrelation | -0.023 | -0.045, -0.003 | -0.045, -0.004 | -0.175, 0.157 | -0.185, 0.164 |
| v4-minus-simple | netSDRatio | 0.119 | 0.099, 0.146 | 0.099, 0.147 | -0.046, 0.281 | -0.047, 0.287 |
| v4-minus-simple | calibrationSlope | -0.084 | -0.108, -0.064 | -0.107, -0.064 | -0.236, 0.096 | -0.243, 0.097 |
| v4-minus-simple | winMAE | -0.474 | -0.690, -0.237 | -0.680, -0.244 | -2.183, 1.178 | -2.196, 1.154 |
| v4-minus-simple | winRMSE | -0.573 | -0.759, -0.307 | -0.753, -0.316 | -2.521, 1.467 | -2.499, 1.507 |
| v4-minus-simple | winSlope | -0.325 | -0.350, -0.297 | -0.351, -0.298 | -0.403, -0.274 | -0.412, -0.263 |
| v4-minus-simple | calibrationError | 0.084 | 0.064, 0.108 | 0.064, 0.107 | -0.096, 0.236 | -0.096, 0.243 |
| v4-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-shrink | netRMSE | 1.027 | — | 0.838, 1.253 | -0.331, 2.159 | -0.309, 2.175 |
| v4-minus-shrink | netCorrelation | -0.023 | — | -0.045, -0.004 | -0.175, 0.157 | -0.185, 0.164 |
| v4-minus-shrink | netSDRatio | 0.318 | — | 0.297, 0.345 | 0.153, 0.491 | 0.145, 0.493 |
| v4-minus-shrink | calibrationSlope | -0.229 | — | -0.253, -0.210 | -0.408, -0.011 | -0.414, -0.011 |
| v4-minus-shrink | winMAE | -0.091 | — | -0.298, 0.139 | -1.586, 1.348 | -1.592, 1.342 |
| v4-minus-shrink | winRMSE | -0.041 | — | -0.220, 0.217 | -1.775, 1.704 | -1.768, 1.742 |
| v4-minus-shrink | winSlope | -0.369 | — | -0.394, -0.342 | -0.434, -0.325 | -0.444, -0.313 |
| v4-minus-shrink | calibrationError | 0.229 | — | 0.210, 0.253 | 0.011, 0.394 | 0.008, 0.390 |
| v4-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-v1 | netRMSE | -0.014 | — | -0.338, 0.296 | -1.365, 1.240 | -1.442, 1.302 |
| v4-minus-v1 | netCorrelation | 0.183 | — | 0.137, 0.235 | 0.006, 0.376 | -0.002, 0.384 |
| v4-minus-v1 | netSDRatio | 0.494 | — | 0.453, 0.535 | 0.312, 0.652 | 0.299, 0.662 |
| v4-minus-v1 | calibrationSlope | -0.144 | — | -0.204, -0.071 | -0.419, 0.148 | -0.430, 0.174 |
| v4-minus-v1 | winMAE | -0.667 | — | -1.067, -0.327 | -2.208, 0.772 | -2.327, 0.817 |
| v4-minus-v1 | winRMSE | -0.831 | — | -1.221, -0.429 | -2.626, 0.793 | -2.755, 0.857 |
| v4-minus-v1 | winSlope | -0.086 | — | -0.142, -0.030 | -0.140, -0.034 | -0.174, 0.001 |
| v4-minus-v1 | calibrationError | 0.144 | — | 0.071, 0.204 | -0.148, 0.358 | -0.174, 0.366 |
| v4-minus-v1 | defenseCorrelation | 0.089 | — | 0.007, 0.193 | -0.270, 0.376 | -0.276, 0.425 |
| v4-minus-v1 | defenseSDRatio | 0.359 | — | 0.281, 0.420 | 0.135, 0.587 | 0.121, 0.600 |
| v4-minus-v1 | residualSD | 0.014 | — | -0.282, 0.296 | -0.260, 0.309 | -0.424, 0.462 |
| v4-minus-v3-signals-off | netRMSE | -0.070 | — | -0.324, 0.171 | -1.261, 1.085 | -1.344, 1.119 |
| v4-minus-v3-signals-off | netCorrelation | 0.192 | — | 0.159, 0.229 | 0.040, 0.358 | 0.036, 0.366 |
| v4-minus-v3-signals-off | netSDRatio | 0.489 | — | 0.466, 0.509 | 0.303, 0.652 | 0.288, 0.657 |
| v4-minus-v3-signals-off | calibrationSlope | -0.126 | — | -0.164, -0.075 | -0.421, 0.165 | -0.424, 0.190 |
| v4-minus-v3-signals-off | winMAE | -0.983 | — | -1.297, -0.683 | -2.337, 0.323 | -2.452, 0.365 |
| v4-minus-v3-signals-off | winRMSE | -1.086 | — | -1.429, -0.756 | -2.633, 0.343 | -2.763, 0.421 |
| v4-minus-v3-signals-off | winSlope | -0.137 | — | -0.188, -0.083 | -0.209, -0.072 | -0.237, -0.040 |
| v4-minus-v3-signals-off | calibrationError | 0.126 | — | 0.075, 0.164 | -0.167, 0.343 | -0.192, 0.349 |
| v4-minus-v3-signals-off | defenseCorrelation | 0.088 | — | 0.030, 0.167 | -0.285, 0.370 | -0.276, 0.407 |
| v4-minus-v3-signals-off | defenseSDRatio | 0.398 | — | 0.323, 0.451 | 0.166, 0.626 | 0.155, 0.635 |
| v4-minus-v3-signals-off | residualSD | 0.679 | — | 0.436, 0.920 | 0.403, 0.968 | 0.264, 1.094 |
| simple-minus-shrink | netRMSE | 0.442 | — | 0.442, 0.442 | 0.104, 0.730 | 0.103, 0.726 |
| simple-minus-shrink | netCorrelation | -0.000 | — | -0.000, -0.000 | -0.000, 0.000 | -0.000, 0.000 |
| simple-minus-shrink | netSDRatio | 0.198 | — | 0.198, 0.198 | 0.165, 0.236 | 0.166, 0.235 |
| simple-minus-shrink | calibrationSlope | -0.146 | — | -0.146, -0.146 | -0.188, -0.093 | -0.188, -0.091 |
| simple-minus-shrink | winMAE | 0.382 | — | 0.382, 0.382 | -0.156, 0.899 | -0.140, 0.884 |
| simple-minus-shrink | winRMSE | 0.533 | — | 0.533, 0.533 | 0.079, 0.907 | 0.086, 0.896 |
| simple-minus-shrink | winSlope | -0.044 | — | -0.044, -0.044 | -0.055, -0.026 | -0.055, -0.026 |
| simple-minus-shrink | calibrationError | 0.146 | — | 0.146, 0.146 | 0.074, 0.176 | 0.071, 0.176 |
| simple-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-v1 | netRMSE | -0.599 | — | -0.822, -0.420 | -2.218, 1.066 | -2.250, 0.995 |
| simple-minus-v1 | netCorrelation | 0.205 | — | 0.169, 0.251 | -0.037, 0.439 | -0.030, 0.443 |
| simple-minus-v1 | netSDRatio | 0.375 | — | 0.333, 0.409 | 0.175, 0.540 | 0.165, 0.548 |
| simple-minus-v1 | calibrationSlope | -0.060 | — | -0.111, 0.005 | -0.386, 0.290 | -0.387, 0.304 |
| simple-minus-v1 | winMAE | -0.193 | — | -0.520, 0.034 | -2.506, 2.098 | -2.550, 1.988 |
| simple-minus-v1 | winRMSE | -0.258 | — | -0.607, 0.021 | -2.863, 2.312 | -2.949, 2.225 |
| simple-minus-v1 | winSlope | 0.239 | — | 0.195, 0.278 | 0.169, 0.332 | 0.149, 0.353 |
| simple-minus-v1 | calibrationError | 0.060 | — | -0.005, 0.111 | -0.290, 0.334 | -0.300, 0.324 |
| simple-minus-v1 | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-v1 | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-v1 | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-v3-signals-off | netRMSE | -0.654 | — | -0.838, -0.508 | -2.269, 1.038 | -2.282, 0.994 |
| simple-minus-v3-signals-off | netCorrelation | 0.215 | — | 0.184, 0.251 | -0.029, 0.446 | -0.022, 0.456 |
| simple-minus-v3-signals-off | netSDRatio | 0.369 | — | 0.345, 0.387 | 0.162, 0.549 | 0.151, 0.549 |
| simple-minus-v3-signals-off | calibrationSlope | -0.042 | — | -0.079, 0.010 | -0.394, 0.333 | -0.396, 0.339 |
| simple-minus-v3-signals-off | winMAE | -0.510 | — | -0.756, -0.313 | -2.752, 1.718 | -2.800, 1.672 |
| simple-minus-v3-signals-off | winRMSE | -0.512 | — | -0.776, -0.336 | -3.057, 1.972 | -3.054, 1.898 |
| simple-minus-v3-signals-off | winSlope | 0.188 | — | 0.144, 0.232 | 0.108, 0.289 | 0.085, 0.305 |
| simple-minus-v3-signals-off | calibrationError | 0.042 | — | -0.010, 0.079 | -0.331, 0.328 | -0.338, 0.321 |
| simple-minus-v3-signals-off | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-v3-signals-off | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-v3-signals-off | residualSD | — | — | —, — | —, — | —, — |
| shrink-minus-v1 | netRMSE | -1.041 | — | -1.264, -0.862 | -2.400, 0.458 | -2.423, 0.424 |
| shrink-minus-v1 | netCorrelation | 0.205 | — | 0.169, 0.251 | -0.037, 0.439 | -0.030, 0.443 |
| shrink-minus-v1 | netSDRatio | 0.177 | — | 0.135, 0.211 | -0.014, 0.333 | -0.029, 0.343 |
| shrink-minus-v1 | calibrationSlope | 0.085 | — | 0.035, 0.151 | -0.252, 0.449 | -0.248, 0.457 |
| shrink-minus-v1 | winMAE | -0.575 | — | -0.902, -0.349 | -2.517, 1.411 | -2.559, 1.300 |
| shrink-minus-v1 | winRMSE | -0.790 | — | -1.140, -0.512 | -3.017, 1.535 | -3.129, 1.421 |
| shrink-minus-v1 | winSlope | 0.283 | — | 0.239, 0.322 | 0.217, 0.364 | 0.197, 0.388 |
| shrink-minus-v1 | calibrationError | -0.085 | — | -0.151, -0.035 | -0.427, 0.207 | -0.442, 0.197 |
| shrink-minus-v1 | defenseCorrelation | — | — | —, — | —, — | —, — |
| shrink-minus-v1 | defenseSDRatio | — | — | —, — | —, — | —, — |
| shrink-minus-v1 | residualSD | — | — | —, — | —, — | —, — |
| shrink-minus-v3-signals-off | netRMSE | -1.096 | — | -1.280, -0.950 | -2.434, 0.426 | -2.463, 0.389 |
| shrink-minus-v3-signals-off | netCorrelation | 0.215 | — | 0.184, 0.251 | -0.029, 0.446 | -0.022, 0.456 |
| shrink-minus-v3-signals-off | netSDRatio | 0.171 | — | 0.146, 0.188 | -0.029, 0.338 | -0.041, 0.341 |
| shrink-minus-v3-signals-off | calibrationSlope | 0.104 | — | 0.066, 0.156 | -0.261, 0.483 | -0.256, 0.490 |
| shrink-minus-v3-signals-off | winMAE | -0.892 | — | -1.139, -0.695 | -2.801, 1.047 | -2.805, 1.000 |
| shrink-minus-v3-signals-off | winRMSE | -1.045 | — | -1.308, -0.868 | -3.221, 1.200 | -3.245, 1.107 |
| shrink-minus-v3-signals-off | winSlope | 0.232 | — | 0.188, 0.275 | 0.156, 0.322 | 0.133, 0.340 |
| shrink-minus-v3-signals-off | calibrationError | -0.104 | — | -0.156, -0.066 | -0.469, 0.200 | -0.474, 0.191 |
| shrink-minus-v3-signals-off | defenseCorrelation | — | — | —, — | —, — | —, — |
| shrink-minus-v3-signals-off | defenseSDRatio | — | — | —, — | —, — | —, — |
| shrink-minus-v3-signals-off | residualSD | — | — | —, — | —, — | —, — |
| v1-minus-v3-signals-off | netRMSE | -0.055 | — | -0.280, 0.156 | -0.345, 0.233 | -0.484, 0.383 |
| v1-minus-v3-signals-off | netCorrelation | 0.009 | — | -0.036, 0.055 | -0.050, 0.075 | -0.082, 0.102 |
| v1-minus-v3-signals-off | netSDRatio | -0.006 | — | -0.047, 0.034 | -0.038, 0.027 | -0.073, 0.059 |
| v1-minus-v3-signals-off | calibrationSlope | 0.018 | — | -0.040, 0.080 | -0.075, 0.117 | -0.130, 0.159 |
| v1-minus-v3-signals-off | winMAE | -0.317 | — | -0.617, 0.023 | -0.703, 0.063 | -0.897, 0.313 |
| v1-minus-v3-signals-off | winRMSE | -0.254 | — | -0.595, 0.041 | -0.635, 0.114 | -0.868, 0.341 |
| v1-minus-v3-signals-off | winSlope | -0.051 | — | -0.111, 0.020 | -0.130, 0.023 | -0.169, 0.067 |
| v1-minus-v3-signals-off | calibrationError | -0.018 | — | -0.080, 0.040 | -0.113, 0.068 | -0.157, 0.118 |
| v1-minus-v3-signals-off | defenseCorrelation | -0.001 | — | -0.101, 0.104 | -0.098, 0.083 | -0.175, 0.167 |
| v1-minus-v3-signals-off | defenseSDRatio | 0.039 | — | -0.028, 0.105 | -0.012, 0.097 | -0.060, 0.142 |
| v1-minus-v3-signals-off | residualSD | 0.665 | — | 0.437, 0.892 | 0.461, 0.857 | 0.324, 1.004 |

## 2024-25，41場

| 比較 | 指標 | 差值 | 舊seed95% | 新seed95% | 球隊95% | 聯合95% |
|---|---|---:|---|---|---|---|
| v3-minus-v4 | netRMSE | -0.051 | -0.292, 0.191 | -0.284, 0.183 | -1.009, 0.748 | -1.088, 0.828 |
| v3-minus-v4 | netCorrelation | -0.051 | -0.078, -0.028 | -0.078, -0.027 | -0.163, 0.052 | -0.174, 0.058 |
| v3-minus-v4 | netSDRatio | -0.164 | -0.206, -0.118 | -0.205, -0.118 | -0.287, -0.049 | -0.298, -0.034 |
| v3-minus-v4 | calibrationSlope | 0.055 | 0.013, 0.093 | 0.015, 0.093 | -0.111, 0.228 | -0.128, 0.244 |
| v3-minus-v4 | winMAE | 0.177 | -0.113, 0.447 | -0.103, 0.437 | -0.452, 0.810 | -0.580, 0.907 |
| v3-minus-v4 | winRMSE | 0.240 | -0.037, 0.516 | -0.032, 0.498 | -0.628, 0.916 | -0.719, 1.048 |
| v3-minus-v4 | winSlope | 0.043 | 0.009, 0.080 | 0.008, 0.080 | 0.003, 0.083 | -0.019, 0.105 |
| v3-minus-v4 | calibrationError | -0.055 | -0.094, -0.013 | -0.093, -0.015 | -0.224, 0.112 | -0.237, 0.128 |
| v3-minus-v4 | defenseCorrelation | -0.026 | -0.094, 0.044 | -0.091, 0.039 | -0.117, 0.103 | -0.153, 0.134 |
| v3-minus-v4 | defenseSDRatio | 0.052 | -0.000, 0.098 | 0.003, 0.100 | -0.071, 0.161 | -0.091, 0.185 |
| v3-minus-v4 | residualSD | -0.588 | -0.859, -0.313 | -0.861, -0.306 | -0.803, -0.376 | -0.998, -0.173 |
| v3-minus-simple | netRMSE | 0.630 | — | 0.473, 0.840 | -0.899, 1.890 | -0.847, 1.919 |
| v3-minus-simple | netCorrelation | -0.076 | — | -0.101, -0.057 | -0.272, 0.120 | -0.280, 0.116 |
| v3-minus-simple | netSDRatio | 0.015 | — | -0.013, 0.052 | -0.129, 0.178 | -0.135, 0.184 |
| v3-minus-simple | calibrationSlope | -0.094 | — | -0.133, -0.066 | -0.350, 0.143 | -0.358, 0.132 |
| v3-minus-simple | winMAE | 0.133 | — | -0.101, 0.386 | -1.137, 1.381 | -1.090, 1.428 |
| v3-minus-simple | winRMSE | 0.376 | — | 0.161, 0.647 | -1.041, 1.845 | -1.012, 1.859 |
| v3-minus-simple | winSlope | -0.198 | — | -0.223, -0.173 | -0.252, -0.161 | -0.264, -0.148 |
| v3-minus-simple | calibrationError | 0.094 | — | 0.066, 0.133 | -0.139, 0.334 | -0.130, 0.346 |
| v3-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-shrink | netRMSE | 0.777 | — | 0.621, 0.987 | -0.703, 2.040 | -0.670, 2.066 |
| v3-minus-shrink | netCorrelation | -0.076 | — | -0.101, -0.057 | -0.272, 0.120 | -0.280, 0.116 |
| v3-minus-shrink | netSDRatio | 0.327 | — | 0.299, 0.364 | 0.186, 0.496 | 0.175, 0.503 |
| v3-minus-shrink | calibrationSlope | -0.492 | — | -0.531, -0.464 | -0.832, -0.177 | -0.830, -0.184 |
| v3-minus-shrink | winMAE | 0.056 | — | -0.177, 0.310 | -0.899, 1.042 | -0.938, 1.104 |
| v3-minus-shrink | winRMSE | 0.521 | — | 0.307, 0.792 | -0.740, 1.710 | -0.761, 1.756 |
| v3-minus-shrink | winSlope | -0.244 | — | -0.270, -0.219 | -0.291, -0.200 | -0.306, -0.188 |
| v3-minus-shrink | calibrationError | 0.149 | — | 0.120, 0.188 | -0.464, 0.533 | -0.482, 0.542 |
| v3-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-v1 | netRMSE | 0.112 | — | -0.182, 0.425 | -1.029, 1.107 | -1.154, 1.154 |
| v3-minus-v1 | netCorrelation | 0.029 | — | -0.011, 0.071 | -0.122, 0.168 | -0.140, 0.181 |
| v3-minus-v1 | netSDRatio | 0.170 | — | 0.120, 0.217 | 0.046, 0.301 | 0.034, 0.319 |
| v3-minus-v1 | calibrationSlope | -0.113 | — | -0.189, -0.036 | -0.309, 0.043 | -0.329, 0.077 |
| v3-minus-v1 | winMAE | -0.313 | — | -0.653, 0.033 | -1.042, 0.375 | -1.173, 0.538 |
| v3-minus-v1 | winRMSE | -0.066 | — | -0.443, 0.303 | -1.101, 0.855 | -1.242, 0.972 |
| v3-minus-v1 | winSlope | -0.021 | — | -0.060, 0.013 | -0.064, 0.025 | -0.096, 0.054 |
| v3-minus-v1 | calibrationError | 0.113 | — | 0.036, 0.189 | -0.087, 0.278 | -0.112, 0.292 |
| v3-minus-v1 | defenseCorrelation | -0.018 | — | -0.085, 0.068 | -0.300, 0.254 | -0.292, 0.283 |
| v3-minus-v1 | defenseSDRatio | 0.305 | — | 0.241, 0.352 | 0.041, 0.568 | 0.034, 0.584 |
| v3-minus-v1 | residualSD | -0.381 | — | -0.721, -0.031 | -0.572, -0.212 | -0.832, 0.042 |
| v3-minus-v3-signals-off | netRMSE | 0.288 | — | 0.018, 0.543 | -0.820, 1.302 | -0.931, 1.346 |
| v3-minus-v3-signals-off | netCorrelation | 0.003 | — | -0.028, 0.041 | -0.152, 0.136 | -0.159, 0.150 |
| v3-minus-v3-signals-off | netSDRatio | 0.181 | — | 0.139, 0.226 | 0.068, 0.292 | 0.058, 0.314 |
| v3-minus-v3-signals-off | calibrationSlope | -0.159 | — | -0.212, -0.094 | -0.376, 0.005 | -0.383, 0.037 |
| v3-minus-v3-signals-off | winMAE | -0.083 | — | -0.503, 0.310 | -0.795, 0.628 | -0.957, 0.803 |
| v3-minus-v3-signals-off | winRMSE | 0.215 | — | -0.146, 0.538 | -0.801, 1.163 | -0.955, 1.299 |
| v3-minus-v3-signals-off | winSlope | -0.015 | — | -0.051, 0.017 | -0.050, 0.016 | -0.079, 0.045 |
| v3-minus-v3-signals-off | calibrationError | 0.159 | — | 0.094, 0.212 | -0.115, 0.327 | -0.144, 0.333 |
| v3-minus-v3-signals-off | defenseCorrelation | -0.108 | — | -0.188, 0.009 | -0.409, 0.159 | -0.401, 0.199 |
| v3-minus-v3-signals-off | defenseSDRatio | 0.366 | — | 0.297, 0.425 | 0.114, 0.617 | 0.105, 0.636 |
| v3-minus-v3-signals-off | residualSD | -0.171 | — | -0.448, 0.117 | -0.386, 0.035 | -0.590, 0.234 |
| v4-minus-simple | netRMSE | 0.681 | 0.553, 0.865 | 0.548, 0.863 | -0.521, 1.683 | -0.485, 1.731 |
| v4-minus-simple | netCorrelation | -0.025 | -0.042, -0.011 | -0.042, -0.010 | -0.173, 0.144 | -0.178, 0.143 |
| v4-minus-simple | netSDRatio | 0.179 | 0.155, 0.210 | 0.154, 0.209 | 0.019, 0.354 | 0.018, 0.355 |
| v4-minus-simple | calibrationSlope | -0.149 | -0.172, -0.132 | -0.172, -0.132 | -0.350, 0.027 | -0.351, 0.029 |
| v4-minus-simple | winMAE | -0.044 | -0.227, 0.199 | -0.227, 0.189 | -1.279, 1.162 | -1.247, 1.169 |
| v4-minus-simple | winRMSE | 0.136 | -0.022, 0.388 | -0.031, 0.374 | -1.066, 1.349 | -1.075, 1.412 |
| v4-minus-simple | winSlope | -0.241 | -0.261, -0.220 | -0.263, -0.220 | -0.285, -0.202 | -0.295, -0.193 |
| v4-minus-simple | calibrationError | 0.149 | 0.132, 0.172 | 0.132, 0.172 | -0.030, 0.317 | -0.033, 0.321 |
| v4-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-shrink | netRMSE | 0.828 | — | 0.696, 1.010 | -0.324, 1.862 | -0.360, 1.947 |
| v4-minus-shrink | netCorrelation | -0.025 | — | -0.042, -0.010 | -0.173, 0.144 | -0.178, 0.143 |
| v4-minus-shrink | netSDRatio | 0.491 | — | 0.465, 0.521 | 0.328, 0.676 | 0.327, 0.676 |
| v4-minus-shrink | calibrationSlope | -0.547 | — | -0.570, -0.530 | -0.864, -0.238 | -0.865, -0.244 |
| v4-minus-shrink | winMAE | -0.120 | — | -0.304, 0.113 | -1.171, 0.876 | -1.165, 0.923 |
| v4-minus-shrink | winRMSE | 0.282 | — | 0.115, 0.520 | -0.809, 1.240 | -0.806, 1.294 |
| v4-minus-shrink | winSlope | -0.288 | — | -0.310, -0.266 | -0.330, -0.246 | -0.339, -0.237 |
| v4-minus-shrink | calibrationError | 0.204 | — | 0.187, 0.227 | -0.347, 0.495 | -0.362, 0.497 |
| v4-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-v1 | netRMSE | 0.163 | — | -0.152, 0.477 | -0.873, 1.074 | -0.968, 1.130 |
| v4-minus-v1 | netCorrelation | 0.081 | — | 0.042, 0.122 | -0.042, 0.205 | -0.047, 0.224 |
| v4-minus-v1 | netSDRatio | 0.334 | — | 0.282, 0.379 | 0.180, 0.495 | 0.166, 0.510 |
| v4-minus-v1 | calibrationSlope | -0.168 | — | -0.241, -0.087 | -0.388, -0.002 | -0.396, 0.037 |
| v4-minus-v1 | winMAE | -0.490 | — | -0.837, -0.153 | -1.445, 0.428 | -1.565, 0.497 |
| v4-minus-v1 | winRMSE | -0.306 | — | -0.686, 0.052 | -1.341, 0.646 | -1.468, 0.730 |
| v4-minus-v1 | winSlope | -0.064 | — | -0.112, -0.022 | -0.111, -0.019 | -0.143, 0.013 |
| v4-minus-v1 | calibrationError | 0.168 | — | 0.087, 0.241 | -0.016, 0.306 | -0.051, 0.317 |
| v4-minus-v1 | defenseCorrelation | 0.008 | — | -0.057, 0.089 | -0.302, 0.282 | -0.299, 0.318 |
| v4-minus-v1 | defenseSDRatio | 0.253 | — | 0.200, 0.296 | 0.019, 0.456 | 0.018, 0.469 |
| v4-minus-v1 | residualSD | 0.207 | — | -0.081, 0.503 | -0.036, 0.453 | -0.224, 0.634 |
| v4-minus-v3-signals-off | netRMSE | 0.339 | — | 0.077, 0.596 | -0.653, 1.237 | -0.747, 1.290 |
| v4-minus-v3-signals-off | netCorrelation | 0.055 | — | 0.018, 0.097 | -0.064, 0.171 | -0.073, 0.187 |
| v4-minus-v3-signals-off | netSDRatio | 0.345 | — | 0.299, 0.384 | 0.199, 0.498 | 0.190, 0.512 |
| v4-minus-v3-signals-off | calibrationSlope | -0.214 | — | -0.260, -0.154 | -0.457, -0.026 | -0.471, -0.001 |
| v4-minus-v3-signals-off | winMAE | -0.260 | — | -0.603, 0.047 | -1.157, 0.652 | -1.267, 0.683 |
| v4-minus-v3-signals-off | winRMSE | -0.025 | — | -0.337, 0.259 | -1.007, 0.906 | -1.083, 0.946 |
| v4-minus-v3-signals-off | winSlope | -0.058 | — | -0.092, -0.027 | -0.101, -0.021 | -0.126, 0.003 |
| v4-minus-v3-signals-off | calibrationError | 0.214 | — | 0.154, 0.261 | -0.013, 0.347 | -0.056, 0.350 |
| v4-minus-v3-signals-off | defenseCorrelation | -0.082 | — | -0.173, 0.048 | -0.405, 0.201 | -0.404, 0.233 |
| v4-minus-v3-signals-off | defenseSDRatio | 0.314 | — | 0.245, 0.371 | 0.088, 0.507 | 0.085, 0.533 |
| v4-minus-v3-signals-off | residualSD | 0.418 | — | 0.163, 0.655 | 0.181, 0.658 | 0.010, 0.813 |
| simple-minus-shrink | netRMSE | 0.148 | — | 0.148, 0.148 | -0.573, 0.828 | -0.590, 0.805 |
| simple-minus-shrink | netCorrelation | 0.000 | — | 0.000, 0.000 | -0.000, 0.000 | -0.000, 0.000 |
| simple-minus-shrink | netSDRatio | 0.311 | — | 0.311, 0.311 | 0.250, 0.385 | 0.250, 0.383 |
| simple-minus-shrink | calibrationSlope | -0.398 | — | -0.398, -0.398 | -0.540, -0.238 | -0.540, -0.240 |
| simple-minus-shrink | winMAE | -0.076 | — | -0.076, -0.076 | -0.735, 0.619 | -0.753, 0.590 |
| simple-minus-shrink | winRMSE | 0.145 | — | 0.145, 0.145 | -0.561, 0.848 | -0.574, 0.816 |
| simple-minus-shrink | winSlope | -0.047 | — | -0.047, -0.047 | -0.067, -0.015 | -0.067, -0.014 |
| simple-minus-shrink | calibrationError | 0.054 | — | 0.054, 0.054 | -0.540, 0.334 | -0.540, 0.333 |
| simple-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-v1 | netRMSE | -0.517 | — | -0.795, -0.308 | -1.708, 0.749 | -1.767, 0.718 |
| simple-minus-v1 | netCorrelation | 0.106 | — | 0.073, 0.145 | -0.072, 0.265 | -0.070, 0.279 |
| simple-minus-v1 | netSDRatio | 0.154 | — | 0.115, 0.181 | -0.018, 0.316 | -0.029, 0.318 |
| simple-minus-v1 | calibrationSlope | -0.018 | — | -0.077, 0.058 | -0.264, 0.225 | -0.256, 0.248 |
| simple-minus-v1 | winMAE | -0.446 | — | -0.689, -0.229 | -1.821, 0.992 | -1.845, 0.881 |
| simple-minus-v1 | winRMSE | -0.442 | — | -0.736, -0.229 | -1.784, 0.927 | -1.878, 0.875 |
| simple-minus-v1 | winSlope | 0.177 | — | 0.135, 0.212 | 0.131, 0.244 | 0.108, 0.264 |
| simple-minus-v1 | calibrationError | 0.018 | — | -0.058, 0.077 | -0.214, 0.213 | -0.243, 0.213 |
| simple-minus-v1 | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-v1 | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-v1 | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-v3-signals-off | netRMSE | -0.342 | — | -0.569, -0.197 | -1.487, 0.897 | -1.540, 0.882 |
| simple-minus-v3-signals-off | netCorrelation | 0.080 | — | 0.056, 0.115 | -0.096, 0.236 | -0.090, 0.251 |
| simple-minus-v3-signals-off | netSDRatio | 0.165 | — | 0.133, 0.189 | 0.008, 0.313 | 0.001, 0.320 |
| simple-minus-v3-signals-off | calibrationSlope | -0.064 | — | -0.101, -0.006 | -0.326, 0.179 | -0.328, 0.213 |
| simple-minus-v3-signals-off | winMAE | -0.216 | — | -0.486, 0.001 | -1.519, 1.187 | -1.578, 1.110 |
| simple-minus-v3-signals-off | winRMSE | -0.161 | — | -0.416, 0.012 | -1.382, 1.095 | -1.468, 1.037 |
| simple-minus-v3-signals-off | winSlope | 0.183 | — | 0.155, 0.206 | 0.147, 0.225 | 0.128, 0.243 |
| simple-minus-v3-signals-off | calibrationError | 0.064 | — | 0.006, 0.101 | -0.200, 0.252 | -0.231, 0.244 |
| simple-minus-v3-signals-off | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-v3-signals-off | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-v3-signals-off | residualSD | — | — | —, — | —, — | —, — |
| shrink-minus-v1 | netRMSE | -0.665 | — | -0.943, -0.455 | -1.468, 0.253 | -1.528, 0.258 |
| shrink-minus-v1 | netCorrelation | 0.106 | — | 0.073, 0.145 | -0.072, 0.265 | -0.070, 0.279 |
| shrink-minus-v1 | netSDRatio | -0.157 | — | -0.197, -0.131 | -0.325, -0.002 | -0.339, -0.003 |
| shrink-minus-v1 | calibrationSlope | 0.380 | — | 0.321, 0.456 | 0.079, 0.705 | 0.077, 0.716 |
| shrink-minus-v1 | winMAE | -0.370 | — | -0.613, -0.153 | -1.315, 0.604 | -1.359, 0.582 |
| shrink-minus-v1 | winRMSE | -0.588 | — | -0.882, -0.374 | -1.426, 0.324 | -1.504, 0.281 |
| shrink-minus-v1 | winSlope | 0.223 | — | 0.182, 0.259 | 0.177, 0.278 | 0.152, 0.301 |
| shrink-minus-v1 | calibrationError | -0.036 | — | -0.113, 0.022 | -0.414, 0.499 | -0.429, 0.490 |
| shrink-minus-v1 | defenseCorrelation | — | — | —, — | —, — | —, — |
| shrink-minus-v1 | defenseSDRatio | — | — | —, — | —, — | —, — |
| shrink-minus-v1 | residualSD | — | — | —, — | —, — | —, — |
| shrink-minus-v3-signals-off | netRMSE | -0.489 | — | -0.716, -0.345 | -1.289, 0.448 | -1.377, 0.467 |
| shrink-minus-v3-signals-off | netCorrelation | 0.080 | — | 0.056, 0.115 | -0.096, 0.236 | -0.090, 0.251 |
| shrink-minus-v3-signals-off | netSDRatio | -0.146 | — | -0.179, -0.122 | -0.295, -0.006 | -0.305, -0.001 |
| shrink-minus-v3-signals-off | calibrationSlope | 0.334 | — | 0.298, 0.392 | 0.024, 0.652 | 0.029, 0.664 |
| shrink-minus-v3-signals-off | winMAE | -0.140 | — | -0.410, 0.077 | -1.076, 0.868 | -1.150, 0.863 |
| shrink-minus-v3-signals-off | winRMSE | -0.306 | — | -0.561, -0.133 | -1.123, 0.566 | -1.220, 0.538 |
| shrink-minus-v3-signals-off | winSlope | 0.230 | — | 0.201, 0.252 | 0.183, 0.273 | 0.167, 0.288 |
| shrink-minus-v3-signals-off | calibrationError | 0.010 | — | -0.048, 0.046 | -0.387, 0.493 | -0.400, 0.496 |
| shrink-minus-v3-signals-off | defenseCorrelation | — | — | —, — | —, — | —, — |
| shrink-minus-v3-signals-off | defenseSDRatio | — | — | —, — | —, — | —, — |
| shrink-minus-v3-signals-off | residualSD | — | — | —, — | —, — | —, — |
| v1-minus-v3-signals-off | netRMSE | 0.176 | — | -0.161, 0.506 | -0.108, 0.467 | -0.324, 0.691 |
| v1-minus-v3-signals-off | netCorrelation | -0.026 | — | -0.072, 0.024 | -0.077, 0.025 | -0.113, 0.059 |
| v1-minus-v3-signals-off | netSDRatio | 0.011 | — | -0.033, 0.054 | -0.023, 0.044 | -0.056, 0.084 |
| v1-minus-v3-signals-off | calibrationSlope | -0.046 | — | -0.134, 0.049 | -0.123, 0.020 | -0.195, 0.090 |
| v1-minus-v3-signals-off | winMAE | 0.230 | — | -0.100, 0.543 | -0.092, 0.538 | -0.333, 0.782 |
| v1-minus-v3-signals-off | winRMSE | 0.281 | — | -0.051, 0.626 | -0.060, 0.589 | -0.288, 0.864 |
| v1-minus-v3-signals-off | winSlope | 0.006 | — | -0.038, 0.052 | -0.045, 0.049 | -0.078, 0.089 |
| v1-minus-v3-signals-off | calibrationError | 0.046 | — | -0.049, 0.134 | -0.083, 0.108 | -0.123, 0.170 |
| v1-minus-v3-signals-off | defenseCorrelation | -0.090 | — | -0.184, 0.031 | -0.200, -0.010 | -0.266, 0.079 |
| v1-minus-v3-signals-off | defenseSDRatio | 0.061 | — | 0.005, 0.115 | 0.022, 0.115 | -0.026, 0.152 |
| v1-minus-v3-signals-off | residualSD | 0.210 | — | -0.102, 0.534 | -0.028, 0.443 | -0.231, 0.635 |

## 2024-25，55場

| 比較 | 指標 | 差值 | 舊seed95% | 新seed95% | 球隊95% | 聯合95% |
|---|---|---:|---|---|---|---|
| v3-minus-v4 | netRMSE | -0.435 | -0.775, -0.077 | -0.789, -0.072 | -1.485, 0.524 | -1.586, 0.634 |
| v3-minus-v4 | netCorrelation | -0.032 | -0.077, 0.007 | -0.077, 0.007 | -0.125, 0.059 | -0.152, 0.070 |
| v3-minus-v4 | netSDRatio | -0.310 | -0.352, -0.263 | -0.355, -0.262 | -0.457, -0.189 | -0.467, -0.176 |
| v3-minus-v4 | calibrationSlope | 0.224 | 0.156, 0.273 | 0.156, 0.276 | 0.047, 0.402 | 0.002, 0.409 |
| v3-minus-v4 | winMAE | -0.037 | -0.277, 0.187 | -0.267, 0.187 | -0.552, 0.465 | -0.615, 0.535 |
| v3-minus-v4 | winRMSE | 0.002 | -0.237, 0.238 | -0.230, 0.244 | -0.607, 0.577 | -0.670, 0.674 |
| v3-minus-v4 | winSlope | 0.057 | 0.036, 0.079 | 0.036, 0.080 | 0.022, 0.091 | 0.007, 0.107 |
| v3-minus-v4 | calibrationError | -0.224 | -0.274, -0.157 | -0.276, -0.155 | -0.335, 0.019 | -0.344, 0.043 |
| v3-minus-v4 | defenseCorrelation | -0.040 | -0.111, 0.037 | -0.112, 0.033 | -0.201, 0.132 | -0.229, 0.151 |
| v3-minus-v4 | defenseSDRatio | -0.052 | -0.097, -0.003 | -0.098, -0.003 | -0.166, 0.052 | -0.180, 0.069 |
| v3-minus-v4 | residualSD | -0.611 | -0.962, -0.265 | -0.940, -0.258 | -0.955, -0.246 | -1.141, -0.048 |
| v3-minus-simple | netRMSE | 0.376 | — | 0.146, 0.680 | -1.178, 1.684 | -1.184, 1.781 |
| v3-minus-simple | netCorrelation | -0.060 | — | -0.106, -0.026 | -0.271, 0.167 | -0.293, 0.167 |
| v3-minus-simple | netSDRatio | -0.065 | — | -0.094, -0.021 | -0.216, 0.120 | -0.223, 0.127 |
| v3-minus-simple | calibrationSlope | -0.007 | — | -0.079, 0.045 | -0.365, 0.294 | -0.401, 0.282 |
| v3-minus-simple | winMAE | -0.321 | — | -0.491, -0.071 | -1.258, 0.582 | -1.233, 0.643 |
| v3-minus-simple | winRMSE | 0.001 | — | -0.149, 0.229 | -1.091, 1.065 | -1.062, 1.122 |
| v3-minus-simple | winSlope | -0.115 | — | -0.135, -0.095 | -0.156, -0.074 | -0.167, -0.064 |
| v3-minus-simple | calibrationError | 0.007 | — | -0.044, 0.079 | -0.236, 0.290 | -0.235, 0.321 |
| v3-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-shrink | netRMSE | 0.311 | — | 0.080, 0.615 | -1.112, 1.407 | -1.090, 1.525 |
| v3-minus-shrink | netCorrelation | -0.060 | — | -0.106, -0.026 | -0.271, 0.167 | -0.293, 0.167 |
| v3-minus-shrink | netSDRatio | 0.206 | — | 0.176, 0.249 | 0.076, 0.373 | 0.072, 0.385 |
| v3-minus-shrink | calibrationSlope | -0.453 | — | -0.525, -0.402 | -0.931, -0.083 | -0.957, -0.093 |
| v3-minus-shrink | winMAE | -0.338 | — | -0.508, -0.088 | -1.081, 0.369 | -1.075, 0.437 |
| v3-minus-shrink | winRMSE | 0.001 | — | -0.149, 0.230 | -0.898, 0.875 | -0.880, 0.938 |
| v3-minus-shrink | winSlope | -0.148 | — | -0.168, -0.129 | -0.184, -0.101 | -0.195, -0.094 |
| v3-minus-shrink | calibrationError | -0.159 | — | -0.211, -0.088 | -0.690, 0.381 | -0.708, 0.399 |
| v3-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-v1 | netRMSE | -0.100 | — | -0.392, 0.216 | -1.035, 0.790 | -1.145, 0.894 |
| v3-minus-v1 | netCorrelation | 0.024 | — | -0.027, 0.076 | -0.147, 0.149 | -0.164, 0.177 |
| v3-minus-v1 | netSDRatio | 0.075 | — | 0.025, 0.118 | -0.015, 0.170 | -0.036, 0.192 |
| v3-minus-v1 | calibrationSlope | -0.060 | — | -0.133, 0.025 | -0.409, 0.105 | -0.424, 0.150 |
| v3-minus-v1 | winMAE | -0.327 | — | -0.610, -0.037 | -0.788, 0.155 | -0.937, 0.287 |
| v3-minus-v1 | winRMSE | -0.236 | — | -0.528, 0.057 | -0.914, 0.447 | -1.041, 0.534 |
| v3-minus-v1 | winSlope | 0.034 | — | -0.001, 0.067 | -0.011, 0.081 | -0.034, 0.100 |
| v3-minus-v1 | calibrationError | 0.060 | — | -0.025, 0.130 | -0.313, 0.234 | -0.313, 0.258 |
| v3-minus-v1 | defenseCorrelation | 0.057 | — | -0.010, 0.145 | -0.166, 0.283 | -0.205, 0.324 |
| v3-minus-v1 | defenseSDRatio | 0.144 | — | 0.076, 0.207 | -0.082, 0.350 | -0.085, 0.368 |
| v3-minus-v1 | residualSD | -0.259 | — | -0.653, 0.127 | -0.477, -0.033 | -0.762, 0.250 |
| v3-minus-v3-signals-off | netRMSE | -0.499 | — | -0.848, -0.178 | -1.293, 0.289 | -1.443, 0.406 |
| v3-minus-v3-signals-off | netCorrelation | 0.082 | — | 0.035, 0.131 | -0.053, 0.212 | -0.074, 0.231 |
| v3-minus-v3-signals-off | netSDRatio | 0.025 | — | -0.019, 0.065 | -0.056, 0.102 | -0.077, 0.124 |
| v3-minus-v3-signals-off | calibrationSlope | 0.087 | — | 0.002, 0.181 | -0.126, 0.276 | -0.153, 0.320 |
| v3-minus-v3-signals-off | winMAE | -0.320 | — | -0.630, -0.023 | -0.717, 0.073 | -0.892, 0.225 |
| v3-minus-v3-signals-off | winRMSE | -0.266 | — | -0.570, 0.015 | -0.841, 0.376 | -0.989, 0.478 |
| v3-minus-v3-signals-off | winSlope | 0.016 | — | -0.018, 0.051 | -0.009, 0.047 | -0.038, 0.075 |
| v3-minus-v3-signals-off | calibrationError | -0.087 | — | -0.181, -0.002 | -0.261, 0.118 | -0.295, 0.138 |
| v3-minus-v3-signals-off | defenseCorrelation | 0.083 | — | -0.006, 0.185 | -0.176, 0.338 | -0.195, 0.379 |
| v3-minus-v3-signals-off | defenseSDRatio | 0.145 | — | 0.084, 0.193 | -0.087, 0.356 | -0.090, 0.372 |
| v3-minus-v3-signals-off | residualSD | 0.159 | — | -0.233, 0.552 | -0.090, 0.412 | -0.350, 0.682 |
| v4-minus-simple | netRMSE | 0.811 | 0.571, 1.138 | 0.563, 1.152 | -0.665, 1.998 | -0.657, 2.120 |
| v4-minus-simple | netCorrelation | -0.028 | -0.052, -0.010 | -0.054, -0.009 | -0.196, 0.161 | -0.203, 0.159 |
| v4-minus-simple | netSDRatio | 0.246 | 0.205, 0.298 | 0.205, 0.301 | 0.080, 0.453 | 0.069, 0.471 |
| v4-minus-simple | calibrationSlope | -0.231 | -0.273, -0.197 | -0.276, -0.195 | -0.490, -0.027 | -0.491, -0.020 |
| v4-minus-simple | winMAE | -0.284 | -0.458, -0.051 | -0.464, -0.051 | -1.096, 0.506 | -1.099, 0.571 |
| v4-minus-simple | winRMSE | -0.001 | -0.146, 0.197 | -0.147, 0.200 | -0.918, 0.835 | -0.900, 0.887 |
| v4-minus-simple | winSlope | -0.172 | -0.185, -0.157 | -0.185, -0.156 | -0.205, -0.136 | -0.212, -0.131 |
| v4-minus-simple | calibrationError | 0.231 | 0.197, 0.273 | 0.195, 0.276 | -0.028, 0.393 | -0.034, 0.408 |
| v4-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-shrink | netRMSE | 0.745 | — | 0.497, 1.087 | -0.779, 2.140 | -0.769, 2.228 |
| v4-minus-shrink | netCorrelation | -0.028 | — | -0.054, -0.009 | -0.196, 0.161 | -0.203, 0.159 |
| v4-minus-shrink | netSDRatio | 0.516 | — | 0.475, 0.571 | 0.340, 0.742 | 0.329, 0.756 |
| v4-minus-shrink | calibrationSlope | -0.678 | — | -0.723, -0.641 | -1.073, -0.354 | -1.078, -0.353 |
| v4-minus-shrink | winMAE | -0.302 | — | -0.482, -0.068 | -1.092, 0.482 | -1.067, 0.557 |
| v4-minus-shrink | winRMSE | -0.001 | — | -0.147, 0.200 | -0.875, 0.783 | -0.842, 0.849 |
| v4-minus-shrink | winSlope | -0.205 | — | -0.219, -0.189 | -0.236, -0.165 | -0.243, -0.160 |
| v4-minus-shrink | calibrationError | 0.065 | — | 0.029, 0.110 | -0.581, 0.521 | -0.590, 0.521 |
| v4-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-v1 | netRMSE | 0.335 | — | -0.013, 0.657 | -0.874, 1.429 | -0.971, 1.460 |
| v4-minus-v1 | netCorrelation | 0.056 | — | 0.007, 0.116 | -0.086, 0.176 | -0.094, 0.200 |
| v4-minus-v1 | netSDRatio | 0.385 | — | 0.332, 0.430 | 0.229, 0.557 | 0.212, 0.571 |
| v4-minus-v1 | calibrationSlope | -0.285 | — | -0.346, -0.192 | -0.654, -0.080 | -0.661, -0.047 |
| v4-minus-v1 | winMAE | -0.290 | — | -0.610, 0.003 | -1.073, 0.513 | -1.175, 0.575 |
| v4-minus-v1 | winRMSE | -0.238 | — | -0.545, 0.048 | -1.059, 0.570 | -1.172, 0.622 |
| v4-minus-v1 | winSlope | -0.023 | — | -0.048, 0.000 | -0.056, 0.012 | -0.076, 0.026 |
| v4-minus-v1 | calibrationError | 0.285 | — | 0.192, 0.341 | -0.258, 0.395 | -0.240, 0.399 |
| v4-minus-v1 | defenseCorrelation | 0.097 | — | 0.007, 0.198 | -0.162, 0.367 | -0.187, 0.405 |
| v4-minus-v1 | defenseSDRatio | 0.196 | — | 0.141, 0.241 | -0.014, 0.401 | -0.023, 0.413 |
| v4-minus-v1 | residualSD | 0.352 | — | 0.027, 0.664 | 0.022, 0.699 | -0.193, 0.884 |
| v4-minus-v3-signals-off | netRMSE | -0.064 | — | -0.378, 0.260 | -1.082, 0.901 | -1.172, 1.000 |
| v4-minus-v3-signals-off | netCorrelation | 0.114 | — | 0.085, 0.149 | 0.002, 0.239 | -0.004, 0.248 |
| v4-minus-v3-signals-off | netSDRatio | 0.335 | — | 0.279, 0.392 | 0.182, 0.487 | 0.167, 0.508 |
| v4-minus-v3-signals-off | calibrationSlope | -0.137 | — | -0.199, -0.059 | -0.386, 0.066 | -0.400, 0.091 |
| v4-minus-v3-signals-off | winMAE | -0.283 | — | -0.587, -0.013 | -0.933, 0.347 | -1.042, 0.437 |
| v4-minus-v3-signals-off | winRMSE | -0.268 | — | -0.525, -0.048 | -0.976, 0.379 | -1.033, 0.456 |
| v4-minus-v3-signals-off | winSlope | -0.041 | — | -0.064, -0.019 | -0.062, -0.016 | -0.082, 0.005 |
| v4-minus-v3-signals-off | calibrationError | 0.137 | — | 0.059, 0.199 | -0.094, 0.286 | -0.120, 0.302 |
| v4-minus-v3-signals-off | defenseCorrelation | 0.122 | — | 0.042, 0.206 | -0.165, 0.414 | -0.172, 0.449 |
| v4-minus-v3-signals-off | defenseSDRatio | 0.197 | — | 0.133, 0.249 | -0.015, 0.405 | -0.035, 0.421 |
| v4-minus-v3-signals-off | residualSD | 0.771 | — | 0.417, 1.152 | 0.386, 1.145 | 0.188, 1.333 |
| simple-minus-shrink | netRMSE | -0.065 | — | -0.065, -0.065 | -0.624, 0.561 | -0.635, 0.542 |
| simple-minus-shrink | netCorrelation | 0.000 | — | 0.000, 0.000 | -0.000, 0.000 | -0.000, 0.000 |
| simple-minus-shrink | netSDRatio | 0.271 | — | 0.271, 0.271 | 0.202, 0.348 | 0.202, 0.350 |
| simple-minus-shrink | calibrationSlope | -0.447 | — | -0.447, -0.447 | -0.614, -0.283 | -0.615, -0.289 |
| simple-minus-shrink | winMAE | -0.018 | — | -0.018, -0.018 | -0.468, 0.445 | -0.459, 0.424 |
| simple-minus-shrink | winRMSE | 0.000 | — | 0.000, 0.000 | -0.446, 0.437 | -0.427, 0.413 |
| simple-minus-shrink | winSlope | -0.033 | — | -0.033, -0.033 | -0.050, -0.007 | -0.050, -0.007 |
| simple-minus-shrink | calibrationError | -0.166 | — | -0.166, -0.166 | -0.614, 0.328 | -0.615, 0.328 |
| simple-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-v1 | netRMSE | -0.476 | — | -0.850, -0.191 | -1.516, 0.670 | -1.627, 0.658 |
| simple-minus-v1 | netCorrelation | 0.085 | — | 0.038, 0.147 | -0.100, 0.227 | -0.102, 0.260 |
| simple-minus-v1 | netSDRatio | 0.139 | — | 0.096, 0.168 | -0.064, 0.321 | -0.070, 0.325 |
| simple-minus-v1 | calibrationSlope | -0.053 | — | -0.126, 0.060 | -0.465, 0.228 | -0.441, 0.261 |
| simple-minus-v1 | winMAE | -0.006 | — | -0.292, 0.184 | -0.931, 0.922 | -1.003, 0.867 |
| simple-minus-v1 | winRMSE | -0.237 | — | -0.550, 0.001 | -1.111, 0.692 | -1.195, 0.662 |
| simple-minus-v1 | winSlope | 0.149 | — | 0.116, 0.176 | 0.106, 0.192 | 0.089, 0.206 |
| simple-minus-v1 | calibrationError | 0.053 | — | -0.060, 0.122 | -0.351, 0.227 | -0.350, 0.224 |
| simple-minus-v1 | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-v1 | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-v1 | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-v3-signals-off | netRMSE | -0.875 | — | -1.119, -0.719 | -1.918, 0.433 | -2.026, 0.385 |
| simple-minus-v3-signals-off | netCorrelation | 0.143 | — | 0.118, 0.177 | -0.066, 0.328 | -0.060, 0.346 |
| simple-minus-v3-signals-off | netSDRatio | 0.090 | — | 0.056, 0.110 | -0.120, 0.262 | -0.133, 0.266 |
| simple-minus-v3-signals-off | calibrationSlope | 0.094 | — | 0.047, 0.166 | -0.223, 0.431 | -0.214, 0.446 |
| simple-minus-v3-signals-off | winMAE | 0.001 | — | -0.206, 0.104 | -0.891, 0.925 | -0.968, 0.878 |
| simple-minus-v3-signals-off | winRMSE | -0.267 | — | -0.464, -0.164 | -1.063, 0.620 | -1.131, 0.568 |
| simple-minus-v3-signals-off | winSlope | 0.131 | — | 0.109, 0.153 | 0.098, 0.168 | 0.085, 0.182 |
| simple-minus-v3-signals-off | calibrationError | -0.094 | — | -0.166, -0.047 | -0.363, 0.169 | -0.392, 0.162 |
| simple-minus-v3-signals-off | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-v3-signals-off | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-v3-signals-off | residualSD | — | — | —, — | —, — | —, — |
| shrink-minus-v1 | netRMSE | -0.410 | — | -0.784, -0.125 | -1.295, 0.548 | -1.410, 0.559 |
| shrink-minus-v1 | netCorrelation | 0.085 | — | 0.038, 0.147 | -0.100, 0.227 | -0.102, 0.260 |
| shrink-minus-v1 | netSDRatio | -0.131 | — | -0.174, -0.103 | -0.326, 0.029 | -0.332, 0.028 |
| shrink-minus-v1 | calibrationSlope | 0.393 | — | 0.320, 0.506 | -0.024, 0.773 | -0.008, 0.794 |
| shrink-minus-v1 | winMAE | 0.012 | — | -0.275, 0.202 | -0.637, 0.669 | -0.739, 0.641 |
| shrink-minus-v1 | winRMSE | -0.237 | — | -0.550, 0.001 | -0.831, 0.416 | -0.943, 0.405 |
| shrink-minus-v1 | winSlope | 0.182 | — | 0.149, 0.210 | 0.139, 0.220 | 0.123, 0.235 |
| shrink-minus-v1 | calibrationError | 0.220 | — | 0.107, 0.288 | -0.366, 0.665 | -0.395, 0.661 |
| shrink-minus-v1 | defenseCorrelation | — | — | —, — | —, — | —, — |
| shrink-minus-v1 | defenseSDRatio | — | — | —, — | —, — | —, — |
| shrink-minus-v1 | residualSD | — | — | —, — | —, — | —, — |
| shrink-minus-v3-signals-off | netRMSE | -0.810 | — | -1.053, -0.653 | -1.757, 0.373 | -1.835, 0.292 |
| shrink-minus-v3-signals-off | netCorrelation | 0.143 | — | 0.118, 0.177 | -0.066, 0.328 | -0.060, 0.346 |
| shrink-minus-v3-signals-off | netSDRatio | -0.181 | — | -0.214, -0.161 | -0.382, -0.026 | -0.390, -0.026 |
| shrink-minus-v3-signals-off | calibrationSlope | 0.540 | — | 0.494, 0.613 | 0.189, 0.983 | 0.196, 0.996 |
| shrink-minus-v3-signals-off | winMAE | 0.018 | — | -0.188, 0.122 | -0.648, 0.749 | -0.713, 0.702 |
| shrink-minus-v3-signals-off | winRMSE | -0.267 | — | -0.464, -0.164 | -0.818, 0.409 | -0.898, 0.395 |
| shrink-minus-v3-signals-off | winSlope | 0.164 | — | 0.142, 0.186 | 0.127, 0.196 | 0.117, 0.211 |
| shrink-minus-v3-signals-off | calibrationError | 0.072 | — | -0.000, 0.119 | -0.489, 0.694 | -0.503, 0.678 |
| shrink-minus-v3-signals-off | defenseCorrelation | — | — | —, — | —, — | —, — |
| shrink-minus-v3-signals-off | defenseSDRatio | — | — | —, — | —, — | —, — |
| shrink-minus-v3-signals-off | residualSD | — | — | —, — | —, — | —, — |
| v1-minus-v3-signals-off | netRMSE | -0.399 | — | -0.761, -0.034 | -0.833, 0.064 | -1.040, 0.324 |
| v1-minus-v3-signals-off | netCorrelation | 0.058 | — | -0.001, 0.112 | -0.011, 0.155 | -0.052, 0.188 |
| v1-minus-v3-signals-off | netSDRatio | -0.050 | — | -0.088, -0.009 | -0.119, 0.007 | -0.147, 0.036 |
| v1-minus-v3-signals-off | calibrationSlope | 0.147 | — | 0.031, 0.245 | 0.012, 0.436 | -0.053, 0.470 |
| v1-minus-v3-signals-off | winMAE | 0.007 | — | -0.283, 0.313 | -0.307, 0.305 | -0.482, 0.513 |
| v1-minus-v3-signals-off | winRMSE | -0.030 | — | -0.380, 0.318 | -0.309, 0.233 | -0.540, 0.485 |
| v1-minus-v3-signals-off | winSlope | -0.018 | — | -0.053, 0.018 | -0.053, 0.019 | -0.077, 0.045 |
| v1-minus-v3-signals-off | calibrationError | -0.147 | — | -0.242, -0.031 | -0.305, 0.313 | -0.333, 0.311 |
| v1-minus-v3-signals-off | defenseCorrelation | 0.026 | — | -0.097, 0.139 | -0.067, 0.119 | -0.172, 0.214 |
| v1-minus-v3-signals-off | defenseSDRatio | 0.001 | — | -0.051, 0.053 | -0.074, 0.072 | -0.105, 0.103 |
| v1-minus-v3-signals-off | residualSD | 0.419 | — | 0.049, 0.778 | 0.206, 0.636 | -0.108, 0.922 |

## 2025-26，25場

| 比較 | 指標 | 差值 | 舊seed95% | 新seed95% | 球隊95% | 聯合95% |
|---|---|---:|---|---|---|---|
| v3-minus-v4 | netRMSE | 1.169 | 0.896, 1.441 | 0.897, 1.444 | 0.104, 2.110 | 0.022, 2.168 |
| v3-minus-v4 | netCorrelation | -0.266 | -0.303, -0.233 | -0.303, -0.233 | -0.455, -0.137 | -0.460, -0.130 |
| v3-minus-v4 | netSDRatio | -0.388 | -0.426, -0.346 | -0.424, -0.348 | -0.493, -0.276 | -0.510, -0.266 |
| v3-minus-v4 | calibrationSlope | 0.005 | -0.055, 0.061 | -0.054, 0.059 | -0.337, 0.243 | -0.334, 0.251 |
| v3-minus-v4 | winMAE | 2.163 | 1.710, 2.623 | 1.690, 2.647 | 1.072, 3.230 | 0.928, 3.383 |
| v3-minus-v4 | winRMSE | 2.418 | 1.925, 2.892 | 1.907, 2.902 | 1.288, 3.515 | 1.132, 3.636 |
| v3-minus-v4 | winSlope | 0.122 | 0.064, 0.175 | 0.066, 0.177 | 0.085, 0.152 | 0.043, 0.201 |
| v3-minus-v4 | calibrationError | -0.005 | -0.061, 0.055 | -0.059, 0.054 | -0.217, 0.337 | -0.223, 0.334 |
| v3-minus-v4 | defenseCorrelation | -0.012 | -0.061, 0.035 | -0.059, 0.033 | -0.111, 0.076 | -0.135, 0.098 |
| v3-minus-v4 | defenseSDRatio | -0.004 | -0.053, 0.044 | -0.054, 0.045 | -0.081, 0.093 | -0.105, 0.113 |
| v3-minus-v4 | residualSD | -1.126 | -1.356, -0.908 | -1.359, -0.922 | -1.348, -0.911 | -1.494, -0.763 |
| v3-minus-simple | netRMSE | 0.830 | — | 0.681, 1.018 | -0.454, 2.138 | -0.482, 2.120 |
| v3-minus-simple | netCorrelation | -0.206 | — | -0.236, -0.182 | -0.442, -0.028 | -0.449, -0.022 |
| v3-minus-simple | netSDRatio | -0.302 | — | -0.329, -0.268 | -0.570, -0.016 | -0.574, -0.016 |
| v3-minus-simple | calibrationSlope | 0.005 | — | -0.047, 0.051 | -0.360, 0.295 | -0.374, 0.300 |
| v3-minus-simple | winMAE | 0.878 | — | 0.571, 1.198 | -1.068, 2.983 | -1.129, 2.958 |
| v3-minus-simple | winRMSE | 0.735 | — | 0.440, 1.099 | -1.022, 2.726 | -1.107, 2.727 |
| v3-minus-simple | winSlope | -0.348 | — | -0.393, -0.302 | -0.472, -0.253 | -0.485, -0.234 |
| v3-minus-simple | calibrationError | -0.005 | — | -0.051, 0.048 | -0.259, 0.355 | -0.270, 0.374 |
| v3-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-shrink | netRMSE | 1.235 | — | 1.085, 1.423 | 0.204, 2.178 | 0.167, 2.243 |
| v3-minus-shrink | netCorrelation | -0.206 | — | -0.236, -0.182 | -0.442, -0.028 | -0.449, -0.022 |
| v3-minus-shrink | netSDRatio | 0.148 | — | 0.121, 0.182 | -0.049, 0.370 | -0.052, 0.370 |
| v3-minus-shrink | calibrationSlope | -0.501 | — | -0.553, -0.455 | -0.952, -0.185 | -0.953, -0.174 |
| v3-minus-shrink | winMAE | 1.399 | — | 1.093, 1.719 | 0.053, 2.756 | -0.004, 2.828 |
| v3-minus-shrink | winRMSE | 1.490 | — | 1.196, 1.855 | 0.085, 2.863 | 0.006, 2.960 |
| v3-minus-shrink | winSlope | -0.505 | — | -0.550, -0.459 | -0.601, -0.436 | -0.615, -0.415 |
| v3-minus-shrink | calibrationError | 0.098 | — | 0.052, 0.150 | -0.429, 0.569 | -0.404, 0.586 |
| v3-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-simple | netRMSE | -0.339 | -0.465, -0.165 | -0.459, -0.167 | -1.282, 0.680 | -1.307, 0.716 |
| v4-minus-simple | netCorrelation | 0.060 | 0.045, 0.072 | 0.045, 0.072 | -0.035, 0.164 | -0.041, 0.164 |
| v4-minus-simple | netSDRatio | 0.086 | 0.065, 0.111 | 0.066, 0.111 | -0.187, 0.388 | -0.195, 0.384 |
| v4-minus-simple | calibrationSlope | 0.001 | -0.019, 0.014 | -0.018, 0.013 | -0.208, 0.163 | -0.201, 0.162 |
| v4-minus-simple | winMAE | -1.285 | -1.515, -1.022 | -1.519, -1.025 | -2.953, 0.450 | -2.965, 0.405 |
| v4-minus-simple | winRMSE | -1.683 | -1.880, -1.399 | -1.878, -1.397 | -3.101, -0.181 | -3.076, -0.165 |
| v4-minus-simple | winSlope | -0.469 | -0.496, -0.443 | -0.495, -0.444 | -0.598, -0.373 | -0.605, -0.364 |
| v4-minus-simple | calibrationError | -0.001 | -0.014, 0.019 | -0.013, 0.018 | -0.161, 0.205 | -0.162, 0.199 |
| v4-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-shrink | netRMSE | 0.066 | — | -0.055, 0.238 | -0.854, 0.990 | -0.849, 1.073 |
| v4-minus-shrink | netCorrelation | 0.060 | — | 0.045, 0.072 | -0.035, 0.164 | -0.041, 0.164 |
| v4-minus-shrink | netSDRatio | 0.536 | — | 0.517, 0.561 | 0.318, 0.786 | 0.319, 0.774 |
| v4-minus-shrink | calibrationSlope | -0.505 | — | -0.524, -0.492 | -0.861, -0.240 | -0.850, -0.255 |
| v4-minus-shrink | winMAE | -0.764 | — | -0.997, -0.504 | -2.203, 0.589 | -2.150, 0.656 |
| v4-minus-shrink | winRMSE | -0.927 | — | -1.122, -0.641 | -2.364, 0.436 | -2.292, 0.527 |
| v4-minus-shrink | winSlope | -0.626 | — | -0.652, -0.601 | -0.725, -0.558 | -0.731, -0.550 |
| v4-minus-shrink | calibrationError | 0.102 | — | 0.089, 0.121 | -0.378, 0.380 | -0.349, 0.394 |
| v4-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-shrink | netRMSE | 0.404 | — | 0.404, 0.404 | -0.475, 1.255 | -0.424, 1.246 |
| simple-minus-shrink | netCorrelation | 0.000 | — | 0.000, 0.000 | -0.000, 0.000 | -0.000, 0.000 |
| simple-minus-shrink | netSDRatio | 0.450 | — | 0.450, 0.450 | 0.344, 0.564 | 0.345, 0.565 |
| simple-minus-shrink | calibrationSlope | -0.506 | — | -0.506, -0.506 | -0.676, -0.366 | -0.662, -0.373 |
| simple-minus-shrink | winMAE | 0.521 | — | 0.521, 0.521 | -0.761, 1.797 | -0.714, 1.793 |
| simple-minus-shrink | winRMSE | 0.756 | — | 0.756, 0.756 | -0.540, 1.926 | -0.448, 1.948 |
| simple-minus-shrink | winSlope | -0.157 | — | -0.157, -0.157 | -0.198, -0.092 | -0.199, -0.093 |
| simple-minus-shrink | calibrationError | 0.103 | — | 0.103, 0.103 | -0.534, 0.412 | -0.482, 0.413 |
| simple-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-shrink | residualSD | — | — | —, — | —, — | —, — |

## 2025-26，41場

| 比較 | 指標 | 差值 | 舊seed95% | 新seed95% | 球隊95% | 聯合95% |
|---|---|---:|---|---|---|---|
| v3-minus-v4 | netRMSE | 1.903 | 1.671, 2.113 | 1.673, 2.123 | 0.947, 2.763 | 0.841, 2.860 |
| v3-minus-v4 | netCorrelation | -0.223 | -0.256, -0.198 | -0.256, -0.198 | -0.366, -0.116 | -0.380, -0.107 |
| v3-minus-v4 | netSDRatio | -0.344 | -0.384, -0.301 | -0.381, -0.302 | -0.438, -0.249 | -0.455, -0.235 |
| v3-minus-v4 | calibrationSlope | 0.114 | 0.051, 0.156 | 0.051, 0.153 | -0.153, 0.396 | -0.169, 0.401 |
| v3-minus-v4 | winMAE | 1.943 | 1.633, 2.273 | 1.630, 2.257 | 1.140, 2.762 | 1.018, 2.845 |
| v3-minus-v4 | winRMSE | 2.100 | 1.785, 2.412 | 1.778, 2.396 | 1.309, 2.853 | 1.140, 2.962 |
| v3-minus-v4 | winSlope | 0.075 | 0.036, 0.111 | 0.037, 0.110 | 0.035, 0.123 | 0.014, 0.148 |
| v3-minus-v4 | calibrationError | -0.114 | -0.146, -0.051 | -0.144, -0.051 | -0.167, 0.352 | -0.173, 0.355 |
| v3-minus-v4 | defenseCorrelation | -0.066 | -0.121, -0.007 | -0.121, -0.007 | -0.190, 0.039 | -0.209, 0.072 |
| v3-minus-v4 | defenseSDRatio | 0.012 | -0.026, 0.051 | -0.027, 0.054 | -0.066, 0.091 | -0.087, 0.109 |
| v3-minus-v4 | residualSD | -0.618 | -0.903, -0.297 | -0.895, -0.302 | -0.881, -0.348 | -1.060, -0.172 |
| v3-minus-simple | netRMSE | 0.892 | — | 0.735, 1.121 | -0.394, 2.160 | -0.387, 2.210 |
| v3-minus-simple | netCorrelation | -0.119 | — | -0.155, -0.095 | -0.324, 0.052 | -0.336, 0.053 |
| v3-minus-simple | netSDRatio | -0.073 | — | -0.087, -0.046 | -0.299, 0.154 | -0.308, 0.158 |
| v3-minus-simple | calibrationSlope | -0.064 | — | -0.130, -0.032 | -0.430, 0.348 | -0.445, 0.328 |
| v3-minus-simple | winMAE | 1.211 | — | 1.044, 1.461 | -0.166, 2.635 | -0.158, 2.708 |
| v3-minus-simple | winRMSE | 1.105 | — | 0.940, 1.338 | -0.273, 2.573 | -0.375, 2.634 |
| v3-minus-simple | winSlope | -0.216 | — | -0.255, -0.177 | -0.299, -0.154 | -0.310, -0.134 |
| v3-minus-simple | calibrationError | -0.031 | — | -0.046, 0.035 | -0.267, 0.338 | -0.256, 0.347 |
| v3-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-shrink | netRMSE | -0.137 | — | -0.293, 0.093 | -1.341, 1.034 | -1.384, 1.105 |
| v3-minus-shrink | netCorrelation | -0.119 | — | -0.155, -0.095 | -0.324, 0.052 | -0.336, 0.053 |
| v3-minus-shrink | netSDRatio | 0.336 | — | 0.321, 0.363 | 0.152, 0.524 | 0.147, 0.528 |
| v3-minus-shrink | calibrationSlope | -1.382 | — | -1.448, -1.349 | -2.061, -0.829 | -2.053, -0.841 |
| v3-minus-shrink | winMAE | -0.008 | — | -0.174, 0.242 | -1.212, 1.144 | -1.196, 1.219 |
| v3-minus-shrink | winRMSE | -0.118 | — | -0.283, 0.115 | -1.385, 1.130 | -1.381, 1.177 |
| v3-minus-shrink | winSlope | -0.309 | — | -0.348, -0.270 | -0.419, -0.224 | -0.430, -0.211 |
| v3-minus-shrink | calibrationError | -1.348 | — | -1.364, -1.283 | -1.978, -0.559 | -1.955, -0.555 |
| v3-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-simple | netRMSE | -1.012 | -1.145, -0.780 | -1.145, -0.764 | -2.299, 0.345 | -2.252, 0.409 |
| v4-minus-simple | netCorrelation | 0.104 | 0.090, 0.113 | 0.089, 0.113 | -0.011, 0.233 | -0.015, 0.229 |
| v4-minus-simple | netSDRatio | 0.271 | 0.244, 0.307 | 0.243, 0.305 | 0.028, 0.509 | 0.019, 0.516 |
| v4-minus-simple | calibrationSlope | -0.178 | -0.213, -0.153 | -0.212, -0.152 | -0.490, 0.092 | -0.488, 0.091 |
| v4-minus-simple | winMAE | -0.732 | -0.909, -0.466 | -0.906, -0.466 | -2.109, 0.602 | -2.074, 0.628 |
| v4-minus-simple | winRMSE | -0.995 | -1.148, -0.751 | -1.145, -0.746 | -2.372, 0.395 | -2.368, 0.432 |
| v4-minus-simple | winSlope | -0.291 | -0.309, -0.273 | -0.309, -0.273 | -0.372, -0.233 | -0.377, -0.226 |
| v4-minus-simple | calibrationError | 0.084 | 0.058, 0.118 | 0.057, 0.117 | -0.290, 0.231 | -0.287, 0.233 |
| v4-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-shrink | netRMSE | -2.040 | — | -2.174, -1.792 | -3.364, -0.532 | -3.347, -0.497 |
| v4-minus-shrink | netCorrelation | 0.104 | — | 0.089, 0.113 | -0.011, 0.233 | -0.015, 0.229 |
| v4-minus-shrink | netSDRatio | 0.680 | — | 0.652, 0.714 | 0.499, 0.871 | 0.487, 0.878 |
| v4-minus-shrink | calibrationSlope | -1.496 | — | -1.530, -1.470 | -2.212, -0.968 | -2.195, -0.968 |
| v4-minus-shrink | winMAE | -1.951 | — | -2.124, -1.684 | -3.354, -0.559 | -3.315, -0.487 |
| v4-minus-shrink | winRMSE | -2.218 | — | -2.368, -1.969 | -3.563, -0.899 | -3.547, -0.782 |
| v4-minus-shrink | winSlope | -0.384 | — | -0.402, -0.366 | -0.495, -0.305 | -0.497, -0.301 |
| v4-minus-shrink | calibrationError | -1.234 | — | -1.261, -1.201 | -2.015, -0.617 | -1.991, -0.621 |
| v4-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-shrink | netRMSE | -1.028 | — | -1.028, -1.028 | -1.736, -0.276 | -1.697, -0.288 |
| simple-minus-shrink | netCorrelation | 0.000 | — | 0.000, 0.000 | -0.000, 0.000 | -0.000, 0.000 |
| simple-minus-shrink | netSDRatio | 0.409 | — | 0.409, 0.409 | 0.312, 0.512 | 0.310, 0.516 |
| simple-minus-shrink | calibrationSlope | -1.318 | — | -1.318, -1.318 | -1.724, -1.018 | -1.718, -1.015 |
| simple-minus-shrink | winMAE | -1.219 | — | -1.219, -1.219 | -2.131, -0.349 | -2.077, -0.324 |
| simple-minus-shrink | winRMSE | -1.223 | — | -1.223, -1.223 | -2.020, -0.484 | -1.978, -0.474 |
| simple-minus-shrink | winSlope | -0.093 | — | -0.093, -0.093 | -0.141, -0.039 | -0.140, -0.042 |
| simple-minus-shrink | calibrationError | -1.318 | — | -1.318, -1.318 | -1.724, -0.636 | -1.718, -0.627 |
| simple-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-shrink | residualSD | — | — | —, — | —, — | —, — |

## 2025-26，55場

| 比較 | 指標 | 差值 | 舊seed95% | 新seed95% | 球隊95% | 聯合95% |
|---|---|---:|---|---|---|---|
| v3-minus-v4 | netRMSE | 1.403 | 1.086, 1.702 | 1.079, 1.693 | 0.369, 2.337 | 0.260, 2.417 |
| v3-minus-v4 | netCorrelation | -0.153 | -0.191, -0.118 | -0.190, -0.118 | -0.296, -0.058 | -0.307, -0.049 |
| v3-minus-v4 | netSDRatio | -0.284 | -0.319, -0.248 | -0.321, -0.247 | -0.383, -0.177 | -0.392, -0.159 |
| v3-minus-v4 | calibrationSlope | 0.130 | 0.059, 0.195 | 0.058, 0.196 | -0.131, 0.351 | -0.154, 0.364 |
| v3-minus-v4 | winMAE | 1.007 | 0.833, 1.183 | 0.833, 1.170 | 0.507, 1.513 | 0.433, 1.588 |
| v3-minus-v4 | winRMSE | 1.175 | 0.920, 1.397 | 0.929, 1.394 | 0.607, 1.721 | 0.515, 1.788 |
| v3-minus-v4 | winSlope | 0.064 | 0.038, 0.093 | 0.037, 0.095 | 0.029, 0.104 | 0.013, 0.121 |
| v3-minus-v4 | calibrationError | -0.130 | -0.153, -0.059 | -0.151, -0.056 | -0.192, 0.250 | -0.196, 0.259 |
| v3-minus-v4 | defenseCorrelation | -0.048 | -0.140, 0.033 | -0.140, 0.035 | -0.153, 0.035 | -0.200, 0.089 |
| v3-minus-v4 | defenseSDRatio | -0.002 | -0.063, 0.054 | -0.063, 0.055 | -0.088, 0.086 | -0.112, 0.119 |
| v3-minus-v4 | residualSD | -0.343 | -0.809, 0.103 | -0.815, 0.111 | -0.593, -0.081 | -0.923, 0.238 |
| v3-minus-simple | netRMSE | 0.843 | — | 0.579, 1.171 | -0.453, 1.970 | -0.486, 2.093 |
| v3-minus-simple | netCorrelation | -0.103 | — | -0.143, -0.070 | -0.284, 0.033 | -0.298, 0.034 |
| v3-minus-simple | netSDRatio | 0.033 | — | 0.003, 0.073 | -0.192, 0.221 | -0.191, 0.231 |
| v3-minus-simple | calibrationSlope | -0.202 | — | -0.284, -0.138 | -0.526, 0.112 | -0.552, 0.119 |
| v3-minus-simple | winMAE | 0.510 | — | 0.347, 0.677 | -0.305, 1.337 | -0.353, 1.374 |
| v3-minus-simple | winRMSE | 0.462 | — | 0.293, 0.694 | -0.458, 1.355 | -0.488, 1.455 |
| v3-minus-simple | winSlope | -0.110 | — | -0.128, -0.090 | -0.157, -0.058 | -0.162, -0.049 |
| v3-minus-simple | calibrationError | -0.181 | — | -0.190, -0.098 | -0.403, 0.270 | -0.410, 0.292 |
| v3-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-shrink | netRMSE | -0.136 | — | -0.400, 0.192 | -1.562, 1.174 | -1.576, 1.248 |
| v3-minus-shrink | netCorrelation | -0.103 | — | -0.143, -0.070 | -0.284, 0.033 | -0.298, 0.034 |
| v3-minus-shrink | netSDRatio | 0.325 | — | 0.295, 0.366 | 0.140, 0.482 | 0.136, 0.494 |
| v3-minus-shrink | calibrationSlope | -1.129 | — | -1.212, -1.066 | -1.627, -0.714 | -1.654, -0.716 |
| v3-minus-shrink | winMAE | -0.123 | — | -0.287, 0.043 | -0.943, 0.651 | -0.971, 0.699 |
| v3-minus-shrink | winRMSE | -0.292 | — | -0.460, -0.060 | -1.222, 0.565 | -1.216, 0.632 |
| v3-minus-shrink | winSlope | -0.140 | — | -0.159, -0.121 | -0.196, -0.079 | -0.200, -0.070 |
| v3-minus-shrink | calibrationError | -1.109 | — | -1.118, -1.026 | -1.538, -0.422 | -1.554, -0.406 |
| v3-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-simple | netRMSE | -0.561 | -0.680, -0.317 | -0.685, -0.323 | -1.845, 0.738 | -1.805, 0.879 |
| v4-minus-simple | netCorrelation | 0.050 | 0.034, 0.059 | 0.034, 0.059 | -0.051, 0.153 | -0.061, 0.152 |
| v4-minus-simple | netSDRatio | 0.317 | 0.297, 0.346 | 0.296, 0.346 | 0.097, 0.509 | 0.085, 0.516 |
| v4-minus-simple | calibrationSlope | -0.332 | -0.360, -0.315 | -0.360, -0.315 | -0.628, -0.066 | -0.641, -0.055 |
| v4-minus-simple | winMAE | -0.497 | -0.600, -0.377 | -0.597, -0.380 | -1.294, 0.273 | -1.297, 0.290 |
| v4-minus-simple | winRMSE | -0.713 | -0.807, -0.524 | -0.803, -0.522 | -1.546, 0.137 | -1.487, 0.194 |
| v4-minus-simple | winSlope | -0.174 | -0.193, -0.157 | -0.193, -0.156 | -0.208, -0.138 | -0.214, -0.131 |
| v4-minus-simple | calibrationError | -0.051 | -0.068, -0.023 | -0.069, -0.023 | -0.386, 0.225 | -0.382, 0.229 |
| v4-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-shrink | netRMSE | -1.540 | — | -1.664, -1.302 | -2.931, 0.047 | -2.884, 0.080 |
| v4-minus-shrink | netCorrelation | 0.050 | — | 0.034, 0.059 | -0.051, 0.153 | -0.061, 0.152 |
| v4-minus-shrink | netSDRatio | 0.609 | — | 0.589, 0.639 | 0.430, 0.773 | 0.417, 0.785 |
| v4-minus-shrink | calibrationSlope | -1.260 | — | -1.288, -1.242 | -1.762, -0.843 | -1.783, -0.831 |
| v4-minus-shrink | winMAE | -1.130 | — | -1.230, -1.013 | -2.014, -0.316 | -2.014, -0.253 |
| v4-minus-shrink | winRMSE | -1.467 | — | -1.556, -1.276 | -2.324, -0.632 | -2.272, -0.563 |
| v4-minus-shrink | winSlope | -0.204 | — | -0.224, -0.186 | -0.250, -0.153 | -0.255, -0.146 |
| v4-minus-shrink | calibrationError | -0.979 | — | -0.996, -0.950 | -1.536, -0.484 | -1.527, -0.476 |
| v4-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-shrink | netRMSE | -0.979 | — | -0.979, -0.979 | -1.582, -0.385 | -1.577, -0.395 |
| simple-minus-shrink | netCorrelation | 0.000 | — | 0.000, 0.000 | -0.000, 0.000 | -0.000, 0.000 |
| simple-minus-shrink | netSDRatio | 0.293 | — | 0.293, 0.293 | 0.231, 0.359 | 0.231, 0.360 |
| simple-minus-shrink | calibrationSlope | -0.928 | — | -0.928, -0.928 | -1.153, -0.743 | -1.156, -0.741 |
| simple-minus-shrink | winMAE | -0.633 | — | -0.633, -0.633 | -1.118, -0.151 | -1.117, -0.147 |
| simple-minus-shrink | winRMSE | -0.754 | — | -0.754, -0.754 | -1.220, -0.323 | -1.209, -0.306 |
| simple-minus-shrink | winSlope | -0.030 | — | -0.030, -0.030 | -0.058, 0.002 | -0.058, 0.004 |
| simple-minus-shrink | calibrationError | -0.928 | — | -0.928, -0.928 | -1.153, -0.650 | -1.156, -0.643 |
| simple-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-shrink | residualSD | — | — | —, — | —, — | —, — |

## combined，25場

| 比較 | 指標 | 差值 | 舊seed95% | 新seed95% | 球隊95% | 聯合95% |
|---|---|---:|---|---|---|---|
| v3-minus-v4 | netRMSE | 0.581 | — | 0.423, 0.727 | -0.160, 1.277 | -0.232, 1.323 |
| v3-minus-v4 | netCorrelation | -0.195 | — | -0.215, -0.176 | -0.314, -0.102 | -0.317, -0.097 |
| v3-minus-v4 | netSDRatio | -0.344 | — | -0.370, -0.315 | -0.443, -0.226 | -0.454, -0.218 |
| v3-minus-v4 | calibrationSlope | 0.030 | — | -0.003, 0.058 | -0.193, 0.212 | -0.201, 0.217 |
| v3-minus-v4 | winMAE | 1.280 | — | 1.020, 1.567 | 0.533, 2.057 | 0.472, 2.155 |
| v3-minus-v4 | winRMSE | 1.530 | — | 1.243, 1.796 | 0.755, 2.358 | 0.666, 2.442 |
| v3-minus-v4 | winSlope | 0.121 | — | 0.075, 0.164 | 0.094, 0.146 | 0.059, 0.183 |
| v3-minus-v4 | calibrationError | -0.030 | — | -0.058, 0.003 | -0.200, 0.193 | -0.204, 0.201 |
| v3-minus-v4 | defenseCorrelation | -0.008 | — | -0.044, 0.029 | -0.071, 0.045 | -0.088, 0.068 |
| v3-minus-v4 | defenseSDRatio | 0.009 | — | -0.028, 0.043 | -0.048, 0.075 | -0.066, 0.089 |
| v3-minus-v4 | residualSD | -0.902 | — | -1.085, -0.716 | -1.107, -0.704 | -1.183, -0.593 |
| v3-minus-simple | netRMSE | 0.726 | — | 0.636, 0.862 | -0.261, 1.600 | -0.309, 1.636 |
| v3-minus-simple | netCorrelation | -0.176 | — | -0.196, -0.162 | -0.333, -0.041 | -0.340, -0.037 |
| v3-minus-simple | netSDRatio | -0.241 | — | -0.260, -0.213 | -0.393, -0.058 | -0.396, -0.052 |
| v3-minus-simple | calibrationSlope | -0.011 | — | -0.045, 0.013 | -0.281, 0.209 | -0.286, 0.211 |
| v3-minus-simple | winMAE | 0.401 | — | 0.226, 0.637 | -0.947, 1.803 | -1.008, 1.817 |
| v3-minus-simple | winRMSE | 0.457 | — | 0.257, 0.722 | -0.798, 1.745 | -0.861, 1.789 |
| v3-minus-simple | winSlope | -0.277 | — | -0.308, -0.246 | -0.359, -0.226 | -0.367, -0.212 |
| v3-minus-simple | calibrationError | 0.011 | — | -0.013, 0.045 | -0.195, 0.281 | -0.193, 0.286 |
| v3-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-shrink | netRMSE | 1.149 | — | 1.059, 1.285 | 0.239, 1.903 | 0.220, 1.939 |
| v3-minus-shrink | netCorrelation | -0.176 | — | -0.196, -0.162 | -0.333, -0.041 | -0.340, -0.037 |
| v3-minus-shrink | netSDRatio | 0.083 | — | 0.064, 0.111 | -0.037, 0.241 | -0.042, 0.249 |
| v3-minus-shrink | calibrationSlope | -0.337 | — | -0.371, -0.313 | -0.627, -0.113 | -0.622, -0.105 |
| v3-minus-shrink | winMAE | 0.852 | — | 0.677, 1.089 | -0.308, 1.965 | -0.314, 1.979 |
| v3-minus-shrink | winRMSE | 1.094 | — | 0.895, 1.359 | -0.097, 2.222 | -0.082, 2.251 |
| v3-minus-shrink | winSlope | -0.377 | — | -0.409, -0.346 | -0.436, -0.341 | -0.446, -0.322 |
| v3-minus-shrink | calibrationError | 0.136 | — | 0.112, 0.169 | -0.199, 0.448 | -0.170, 0.474 |
| v3-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-simple | netRMSE | 0.145 | — | 0.070, 0.268 | -0.656, 0.866 | -0.659, 0.895 |
| v4-minus-simple | netCorrelation | 0.019 | — | 0.009, 0.026 | -0.066, 0.112 | -0.069, 0.111 |
| v4-minus-simple | netSDRatio | 0.103 | — | 0.092, 0.121 | -0.042, 0.262 | -0.043, 0.263 |
| v4-minus-simple | calibrationSlope | -0.041 | — | -0.055, -0.034 | -0.158, 0.060 | -0.158, 0.063 |
| v4-minus-simple | winMAE | -0.879 | — | -1.014, -0.693 | -1.998, 0.206 | -2.020, 0.207 |
| v4-minus-simple | winRMSE | -1.073 | — | -1.164, -0.872 | -2.177, -0.009 | -2.159, 0.025 |
| v4-minus-simple | winSlope | -0.397 | — | -0.420, -0.375 | -0.492, -0.335 | -0.497, -0.329 |
| v4-minus-simple | calibrationError | 0.041 | — | 0.034, 0.055 | -0.060, 0.155 | -0.062, 0.157 |
| v4-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-shrink | netRMSE | 0.568 | — | 0.494, 0.691 | -0.316, 1.351 | -0.259, 1.396 |
| v4-minus-shrink | netCorrelation | 0.019 | — | 0.009, 0.026 | -0.066, 0.112 | -0.069, 0.111 |
| v4-minus-shrink | netSDRatio | 0.427 | — | 0.416, 0.445 | 0.300, 0.572 | 0.298, 0.575 |
| v4-minus-shrink | calibrationSlope | -0.367 | — | -0.380, -0.360 | -0.546, -0.233 | -0.537, -0.230 |
| v4-minus-shrink | winMAE | -0.428 | — | -0.563, -0.241 | -1.509, 0.542 | -1.488, 0.593 |
| v4-minus-shrink | winRMSE | -0.436 | — | -0.527, -0.235 | -1.633, 0.638 | -1.554, 0.713 |
| v4-minus-shrink | winSlope | -0.497 | — | -0.520, -0.475 | -0.566, -0.455 | -0.573, -0.446 |
| v4-minus-shrink | calibrationError | 0.166 | — | 0.159, 0.179 | -0.118, 0.343 | -0.102, 0.349 |
| v4-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-shrink | netRMSE | 0.423 | — | 0.423, 0.423 | -0.023, 0.852 | -0.014, 0.848 |
| simple-minus-shrink | netCorrelation | 0.000 | — | 0.000, 0.000 | -0.000, 0.000 | -0.000, 0.000 |
| simple-minus-shrink | netSDRatio | 0.324 | — | 0.324, 0.324 | 0.265, 0.384 | 0.267, 0.387 |
| simple-minus-shrink | calibrationSlope | -0.326 | — | -0.326, -0.326 | -0.409, -0.255 | -0.403, -0.257 |
| simple-minus-shrink | winMAE | 0.452 | — | 0.452, 0.452 | -0.261, 1.162 | -0.253, 1.172 |
| simple-minus-shrink | winRMSE | 0.637 | — | 0.637, 0.637 | 0.022, 1.240 | 0.044, 1.237 |
| simple-minus-shrink | winSlope | -0.100 | — | -0.100, -0.100 | -0.123, -0.062 | -0.124, -0.063 |
| simple-minus-shrink | calibrationError | 0.124 | — | 0.124, 0.124 | -0.200, 0.282 | -0.182, 0.282 |
| simple-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-shrink | residualSD | — | — | —, — | —, — | —, — |

## combined，41場

| 比較 | 指標 | 差值 | 舊seed95% | 新seed95% | 球隊95% | 聯合95% |
|---|---|---:|---|---|---|---|
| v3-minus-v4 | netRMSE | 0.842 | — | 0.662, 1.016 | 0.161, 1.492 | 0.098, 1.523 |
| v3-minus-v4 | netCorrelation | -0.137 | — | -0.161, -0.118 | -0.241, -0.057 | -0.247, -0.052 |
| v3-minus-v4 | netSDRatio | -0.254 | — | -0.279, -0.225 | -0.339, -0.174 | -0.345, -0.162 |
| v3-minus-v4 | calibrationSlope | 0.085 | — | 0.041, 0.111 | -0.091, 0.254 | -0.101, 0.259 |
| v3-minus-v4 | winMAE | 1.060 | — | 0.845, 1.283 | 0.522, 1.609 | 0.436, 1.664 |
| v3-minus-v4 | winRMSE | 1.128 | — | 0.895, 1.355 | 0.509, 1.713 | 0.416, 1.771 |
| v3-minus-v4 | winSlope | 0.059 | — | 0.033, 0.085 | 0.031, 0.092 | 0.015, 0.109 |
| v3-minus-v4 | calibrationError | -0.085 | — | -0.109, -0.041 | -0.153, 0.166 | -0.160, 0.171 |
| v3-minus-v4 | defenseCorrelation | -0.046 | — | -0.095, 0.004 | -0.127, 0.037 | -0.146, 0.060 |
| v3-minus-v4 | defenseSDRatio | 0.032 | — | -0.002, 0.061 | -0.032, 0.088 | -0.047, 0.103 |
| v3-minus-v4 | residualSD | -0.603 | — | -0.744, -0.462 | -0.790, -0.417 | -0.879, -0.327 |
| v3-minus-simple | netRMSE | 0.761 | — | 0.647, 0.954 | -0.231, 1.674 | -0.269, 1.710 |
| v3-minus-simple | netCorrelation | -0.097 | — | -0.123, -0.081 | -0.257, 0.033 | -0.256, 0.035 |
| v3-minus-simple | netSDRatio | -0.029 | — | -0.042, -0.006 | -0.152, 0.108 | -0.155, 0.109 |
| v3-minus-simple | calibrationSlope | -0.079 | — | -0.125, -0.058 | -0.332, 0.153 | -0.336, 0.149 |
| v3-minus-simple | winMAE | 0.672 | — | 0.540, 0.865 | -0.343, 1.667 | -0.321, 1.671 |
| v3-minus-simple | winRMSE | 0.745 | — | 0.608, 0.955 | -0.320, 1.806 | -0.332, 1.833 |
| v3-minus-simple | winSlope | -0.207 | — | -0.233, -0.181 | -0.264, -0.167 | -0.274, -0.155 |
| v3-minus-simple | calibrationError | 0.032 | — | 0.017, 0.077 | -0.145, 0.276 | -0.131, 0.284 |
| v3-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-shrink | netRMSE | 0.293 | — | 0.179, 0.486 | -0.731, 1.297 | -0.747, 1.333 |
| v3-minus-shrink | netCorrelation | -0.097 | — | -0.123, -0.081 | -0.257, 0.033 | -0.256, 0.035 |
| v3-minus-shrink | netSDRatio | 0.331 | — | 0.318, 0.354 | 0.223, 0.454 | 0.217, 0.456 |
| v3-minus-shrink | calibrationSlope | -0.937 | — | -0.983, -0.916 | -1.307, -0.647 | -1.304, -0.650 |
| v3-minus-shrink | winMAE | 0.024 | — | -0.107, 0.218 | -0.861, 0.882 | -0.878, 0.935 |
| v3-minus-shrink | winRMSE | 0.178 | — | 0.040, 0.388 | -0.811, 1.115 | -0.841, 1.179 |
| v3-minus-shrink | winSlope | -0.277 | — | -0.302, -0.251 | -0.341, -0.226 | -0.349, -0.218 |
| v3-minus-shrink | calibrationError | -0.600 | — | -0.615, -0.554 | -0.990, -0.152 | -0.982, -0.132 |
| v3-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-simple | netRMSE | -0.081 | — | -0.154, 0.055 | -1.042, 0.853 | -0.985, 0.899 |
| v4-minus-simple | netCorrelation | 0.040 | — | 0.030, 0.046 | -0.060, 0.139 | -0.066, 0.141 |
| v4-minus-simple | netSDRatio | 0.225 | — | 0.208, 0.250 | 0.102, 0.369 | 0.098, 0.371 |
| v4-minus-simple | calibrationSlope | -0.164 | — | -0.186, -0.150 | -0.328, -0.034 | -0.329, -0.031 |
| v4-minus-simple | winMAE | -0.388 | — | -0.497, -0.217 | -1.487, 0.605 | -1.433, 0.634 |
| v4-minus-simple | winRMSE | -0.383 | — | -0.484, -0.205 | -1.428, 0.588 | -1.412, 0.634 |
| v4-minus-simple | winSlope | -0.266 | — | -0.282, -0.251 | -0.322, -0.230 | -0.326, -0.225 |
| v4-minus-simple | calibrationError | 0.116 | — | 0.103, 0.138 | -0.107, 0.223 | -0.099, 0.224 |
| v4-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-shrink | netRMSE | -0.549 | — | -0.621, -0.413 | -1.641, 0.510 | -1.582, 0.593 |
| v4-minus-shrink | netCorrelation | 0.040 | — | 0.030, 0.046 | -0.060, 0.139 | -0.066, 0.141 |
| v4-minus-shrink | netSDRatio | 0.585 | — | 0.568, 0.610 | 0.479, 0.717 | 0.471, 0.719 |
| v4-minus-shrink | calibrationSlope | -1.022 | — | -1.044, -1.008 | -1.365, -0.766 | -1.357, -0.762 |
| v4-minus-shrink | winMAE | -1.036 | — | -1.144, -0.864 | -2.076, -0.068 | -2.029, -0.022 |
| v4-minus-shrink | winRMSE | -0.950 | — | -1.051, -0.772 | -2.035, -0.020 | -2.009, 0.066 |
| v4-minus-shrink | winSlope | -0.336 | — | -0.351, -0.320 | -0.400, -0.289 | -0.405, -0.285 |
| v4-minus-shrink | calibrationError | -0.515 | — | -0.529, -0.493 | -0.972, -0.178 | -0.962, -0.168 |
| v4-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-shrink | netRMSE | -0.468 | — | -0.468, -0.468 | -0.992, 0.065 | -0.982, 0.060 |
| simple-minus-shrink | netCorrelation | 0.000 | — | 0.000, 0.000 | -0.000, 0.000 | -0.000, 0.000 |
| simple-minus-shrink | netSDRatio | 0.360 | — | 0.360, 0.360 | 0.298, 0.422 | 0.300, 0.425 |
| simple-minus-shrink | calibrationSlope | -0.858 | — | -0.858, -0.858 | -1.063, -0.704 | -1.053, -0.702 |
| simple-minus-shrink | winMAE | -0.648 | — | -0.648, -0.648 | -1.149, -0.147 | -1.143, -0.160 |
| simple-minus-shrink | winRMSE | -0.567 | — | -0.567, -0.567 | -1.152, 0.004 | -1.119, -0.031 |
| simple-minus-shrink | winSlope | -0.070 | — | -0.070, -0.070 | -0.096, -0.036 | -0.095, -0.038 |
| simple-minus-shrink | calibrationError | -0.632 | — | -0.632, -0.632 | -0.969, -0.285 | -0.960, -0.279 |
| simple-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-shrink | residualSD | — | — | —, — | —, — | —, — |

## combined，55場

| 比較 | 指標 | 差值 | 舊seed95% | 新seed95% | 球隊95% | 聯合95% |
|---|---|---:|---|---|---|---|
| v3-minus-v4 | netRMSE | 0.413 | — | 0.135, 0.663 | -0.432, 1.167 | -0.499, 1.259 |
| v3-minus-v4 | netCorrelation | -0.092 | — | -0.125, -0.061 | -0.185, -0.025 | -0.196, -0.015 |
| v3-minus-v4 | netSDRatio | -0.297 | — | -0.313, -0.277 | -0.395, -0.209 | -0.397, -0.200 |
| v3-minus-v4 | calibrationSlope | 0.177 | — | 0.125, 0.214 | 0.007, 0.316 | -0.011, 0.319 |
| v3-minus-v4 | winMAE | 0.485 | — | 0.333, 0.637 | 0.148, 0.834 | 0.066, 0.884 |
| v3-minus-v4 | winRMSE | 0.563 | — | 0.383, 0.751 | 0.109, 1.011 | 0.036, 1.067 |
| v3-minus-v4 | winSlope | 0.060 | — | 0.045, 0.075 | 0.035, 0.087 | 0.026, 0.097 |
| v3-minus-v4 | calibrationError | -0.177 | — | -0.202, -0.122 | -0.222, 0.061 | -0.230, 0.076 |
| v3-minus-v4 | defenseCorrelation | -0.044 | — | -0.092, 0.008 | -0.136, 0.047 | -0.158, 0.065 |
| v3-minus-v4 | defenseSDRatio | -0.027 | — | -0.065, 0.010 | -0.091, 0.025 | -0.104, 0.047 |
| v3-minus-v4 | residualSD | -0.477 | — | -0.718, -0.251 | -0.699, -0.248 | -0.831, -0.116 |
| v3-minus-simple | netRMSE | 0.606 | — | 0.401, 0.871 | -0.438, 1.552 | -0.445, 1.583 |
| v3-minus-simple | netCorrelation | -0.081 | — | -0.118, -0.054 | -0.236, 0.055 | -0.246, 0.053 |
| v3-minus-simple | netSDRatio | -0.016 | — | -0.034, 0.014 | -0.151, 0.119 | -0.151, 0.128 |
| v3-minus-simple | calibrationSlope | -0.104 | — | -0.171, -0.063 | -0.373, 0.105 | -0.406, 0.109 |
| v3-minus-simple | winMAE | 0.095 | — | -0.035, 0.266 | -0.587, 0.755 | -0.594, 0.794 |
| v3-minus-simple | winRMSE | 0.234 | — | 0.120, 0.418 | -0.524, 1.006 | -0.529, 1.029 |
| v3-minus-simple | winSlope | -0.113 | — | -0.123, -0.101 | -0.141, -0.081 | -0.146, -0.075 |
| v3-minus-simple | calibrationError | -0.087 | — | -0.109, -0.021 | -0.248, 0.193 | -0.245, 0.210 |
| v3-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v3-minus-shrink | netRMSE | 0.081 | — | -0.123, 0.347 | -0.907, 1.031 | -0.928, 1.097 |
| v3-minus-shrink | netCorrelation | -0.081 | — | -0.118, -0.054 | -0.236, 0.055 | -0.246, 0.053 |
| v3-minus-shrink | netSDRatio | 0.266 | — | 0.248, 0.295 | 0.155, 0.381 | 0.153, 0.391 |
| v3-minus-shrink | calibrationSlope | -0.791 | — | -0.858, -0.750 | -1.165, -0.522 | -1.182, -0.521 |
| v3-minus-shrink | winMAE | -0.231 | — | -0.361, -0.059 | -0.825, 0.319 | -0.842, 0.361 |
| v3-minus-shrink | winRMSE | -0.153 | — | -0.267, 0.031 | -0.828, 0.504 | -0.846, 0.560 |
| v3-minus-shrink | winSlope | -0.144 | — | -0.155, -0.133 | -0.173, -0.108 | -0.179, -0.104 |
| v3-minus-shrink | calibrationError | -0.634 | — | -0.656, -0.568 | -0.954, -0.176 | -0.934, -0.167 |
| v3-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v3-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v3-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-simple | netRMSE | 0.193 | — | 0.048, 0.445 | -0.951, 1.175 | -0.874, 1.292 |
| v4-minus-simple | netCorrelation | 0.011 | — | -0.007, 0.022 | -0.097, 0.129 | -0.103, 0.123 |
| v4-minus-simple | netSDRatio | 0.281 | — | 0.263, 0.309 | 0.150, 0.429 | 0.146, 0.436 |
| v4-minus-simple | calibrationSlope | -0.282 | — | -0.311, -0.265 | -0.476, -0.124 | -0.486, -0.122 |
| v4-minus-simple | winMAE | -0.390 | — | -0.499, -0.242 | -1.048, 0.204 | -1.011, 0.246 |
| v4-minus-simple | winRMSE | -0.330 | — | -0.414, -0.165 | -1.062, 0.342 | -1.002, 0.383 |
| v4-minus-simple | winSlope | -0.173 | — | -0.186, -0.159 | -0.199, -0.150 | -0.203, -0.144 |
| v4-minus-simple | calibrationError | 0.090 | — | 0.073, 0.119 | -0.138, 0.245 | -0.121, 0.259 |
| v4-minus-simple | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-simple | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-simple | residualSD | — | — | —, — | —, — | —, — |
| v4-minus-shrink | netRMSE | -0.331 | — | -0.476, -0.079 | -1.533, 0.829 | -1.437, 0.918 |
| v4-minus-shrink | netCorrelation | 0.011 | — | -0.007, 0.022 | -0.097, 0.129 | -0.103, 0.123 |
| v4-minus-shrink | netSDRatio | 0.563 | — | 0.545, 0.590 | 0.436, 0.709 | 0.431, 0.716 |
| v4-minus-shrink | calibrationSlope | -0.969 | — | -0.998, -0.952 | -1.282, -0.721 | -1.292, -0.721 |
| v4-minus-shrink | winMAE | -0.716 | — | -0.824, -0.568 | -1.373, -0.137 | -1.336, -0.082 |
| v4-minus-shrink | winRMSE | -0.717 | — | -0.801, -0.552 | -1.415, -0.084 | -1.364, -0.023 |
| v4-minus-shrink | winSlope | -0.205 | — | -0.218, -0.191 | -0.229, -0.175 | -0.234, -0.171 |
| v4-minus-shrink | calibrationError | -0.457 | — | -0.474, -0.427 | -0.880, -0.089 | -0.869, -0.094 |
| v4-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| v4-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| v4-minus-shrink | residualSD | — | — | —, — | —, — | —, — |
| simple-minus-shrink | netRMSE | -0.524 | — | -0.524, -0.524 | -0.969, -0.072 | -0.963, -0.079 |
| simple-minus-shrink | netCorrelation | 0.000 | — | 0.000, 0.000 | -0.000, 0.000 | -0.000, 0.000 |
| simple-minus-shrink | netSDRatio | 0.282 | — | 0.282, 0.282 | 0.227, 0.338 | 0.228, 0.339 |
| simple-minus-shrink | calibrationSlope | -0.687 | — | -0.687, -0.687 | -0.823, -0.565 | -0.822, -0.569 |
| simple-minus-shrink | winMAE | -0.326 | — | -0.326, -0.326 | -0.690, 0.020 | -0.681, 0.011 |
| simple-minus-shrink | winRMSE | -0.387 | — | -0.387, -0.387 | -0.718, -0.077 | -0.720, -0.088 |
| simple-minus-shrink | winSlope | -0.032 | — | -0.032, -0.032 | -0.048, -0.009 | -0.048, -0.008 |
| simple-minus-shrink | calibrationError | -0.547 | — | -0.547, -0.547 | -0.814, -0.261 | -0.813, -0.266 |
| simple-minus-shrink | defenseCorrelation | — | — | —, — | —, — | —, — |
| simple-minus-shrink | defenseSDRatio | — | — | —, — | —, — | —, — |
| simple-minus-shrink | residualSD | — | — | —, — | —, — | —, — |

