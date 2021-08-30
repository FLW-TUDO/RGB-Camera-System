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
````


