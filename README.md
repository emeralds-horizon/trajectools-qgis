# QGIS Processing Trajectools

[![Project Status: Suspended – Initial development has started, but there has not yet been a stable, usable release; work has been stopped for the time being but the author(s) intend on resuming work.](https://www.repostatus.org/badges/latest/suspended.svg)](https://www.repostatus.org/#suspended)

The Trajectools plugin adds trajectory tools to the QGIS Processing toolbox. 

![Trajectools screenshot](https://raw.githubusercontent.com/anitagraser/qgis-processing-trajectory/master/screenshots/trajectools.PNG)


**Note: This plugin depends on MovingPandas!** You will need to install MovingPandas in your QGIS Python environment. I recommend installing both QGIS and MovingPandas from conda-forge:

```
conda create -n qgis python=3.9
(base) PS C:\Users\anita> conda activate qgis
(qgis) PS C:\Users\anita> mamba install -c conda-forge qgis=3.28.2
(qgis) PS C:\Users\anita> mamba install -c conda-forge movingpandas
```

More details: https://anitagraser.com/2023/01/21/pyqgis-jupyter-notebooks-on-windows-using-conda/


