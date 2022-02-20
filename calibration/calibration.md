# Calibration results [26.08.21]:

## Notes- Trial 1:
- cv.calibrateCamera function is used for intrinsics and extrinsics
- Camera on ground
- Corners covered (depth varied)
- 20 imgs used
- 8x6 chessboard - 130 mm
- Reprojection error (opencv tutorial method): 0.0272


```
mtx = [[864.97264262,   0.0,         633.44876394],
       [  0.0,         864.93841842, 522.59039761],
       [  0.0,          0.0,           1.0,      ]]

 dist = [[-0.17183669,  0.13335938,  0.00132646,  0.00052755, -0.03658966]]
 newcameramtx = [[797.54852295,   0.0         634.32813817],
                 [0.0,         798.67584229,  524.89860113],
                 [0.0,           0.0,            1.0      ]]
```

# Calibration results [31.08.21]:

## Notes:
- 16 images used (filtered with selecter)
- Reprojection error: 0.0256
- Other details as above (26.08.21)

```
mtx = [[856.64715347,   0.0,         628.00868644],
       [  0.0,         857.73796509, 520.2976301],
       [  0.0,          0.0,           1.0,      ]]

 dist = [[-0.18619846,  0.14989978,  0.00036384,  -0.00132873, -0.04512847]]
 newcameramtx = [[784.04003906,   0.0         624.41500984],
                 [0.0,         783.08575439,  521.11914666],
                 [0.0,           0.0,            1.0      ]]
```

# Extrinsic Calibration results [03.09.21]:

## Notes
- Camera location (ground) from calibration images on 31.09.21

```
 cam2vicon_trans_avg = [-5330.06, 485.872, 1128.336]

```
