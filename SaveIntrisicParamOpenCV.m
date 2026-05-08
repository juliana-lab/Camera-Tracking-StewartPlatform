load('cameraParams48.mat')

[intrinsicMatrix,distortionCoefficients] = cameraIntrinsicsToOpenCV(params)

params = struct('IntrinsicMatrix', intrinsicMatrix, 'DistortionCoefficients', distortionCoefficients);
save('cameraParams48.mat', 'params');
