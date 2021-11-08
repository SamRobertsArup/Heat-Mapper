# Heat-Mapper
Creates a heat map from the following *required* folder structure: <br>

/data/AOI <br>
	*yourAreaOfInterest.shp* <br>
/data/Constraints/1 <br>
	*contraintWithMagnitudeOfOne.shp* <br>
	*anotherContraintWithMagnitudeOfOne.shp* <br>
/data/Constraints/2 <br>
	*contraintWithMagnitudeOfTwo.shp* <br>


Mess around with the variables: <br>
+ Raster Magnitude *The higher the number the greater intensity of contraint, think of this like contrast*
+ Smoothness *Applies a gaussian filter to smooth your heatmap, this is the sigma value*

![various magnitudes and smoothnesses](InputSettingsResults.png)