# Heat-Mapper
Creates a heat map from the following *required* folder structure: <br>

/data/AOI/ <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*yourAreaOfInterest.shp* <br>
/data/Constraints/1/ <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*contraintWithMagnitudeOfOne.shp* <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*anotherContraintWithMagnitudeOfOne.shp* <br>
/data/Constraints/2/ <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*contraintWithMagnitudeOfTwo.shp* <br>

You can have as many constraint subfolders *so long as they all have an integer name* as you'd like with as many shapefiles in them as you'd like <br> <br>
Mess around with the variables: <br>
+ Raster Magnitude *The higher the number the greater intensity of contraint, think of this like contrast*
+ Smoothness *Applies a gaussian filter to smooth your heatmap, this is the sigma value*

<br>

![various magnitudes and smoothnesses](https://raw.githubusercontent.com/SamRobertsArup/Heat-Mapper/main/InputSettingsResults.png)
