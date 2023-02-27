from mpl_toolkits import mplot3d
import numpy
import matplotlib.pyplot as plt
import yaml

# Referneces:
# https://jakevdp.github.io/PythonDataScienceHandbook/04.12-three-dimensional-plotting.html
# https://jakevdp.github.io/PythonDataScienceHandbook/04.02-simple-scatter-plots.html

with open("fieldlog.yaml", 'r') as logfile:
    data = yaml.safe_load(logfile)


"""
Variables that would be good to plot:
ping_time
bandwidth
spreading
tx_power
orig_rssi
orig_snr
rssi
snr

Variables that would not be good to plot:
send_time
final_time
test_num
"""
disp = {"x": "spreading", "y": "snr", "log": {"x": False, "y": False, "z": False}}
# disp = {"x": "spreading", "y": "bandwidth", "z": "ping_time", "log": {"x": False, "y": False, "z": False}}


fig = plt.figure()
ax = plt.axes(projection='3d' if "z" in disp.keys() else None)


x = []
y = []
z = []
c = []

# I think it's actually better to build the arrays like this because numpy arrays are immutable
for point in data:
    x.append(point[disp["x"]])
    y.append(point[disp["y"]])
    if "z" in disp.keys():
        z.append(point[disp["z"]])
    if "c" in disp.keys():
        c.append(point[disp["c"]])

x = numpy.array(x)
y = numpy.array(y)
assert x.size == y.size

if "z" in disp.keys():
    z = numpy.array(z)
    assert len(z) == len(x)
if "c" in disp.keys():
    c = numpy.array(c)
    assert len(c) == len(x)

if "z" in disp.keys():
    if "c" in disp.keys():
        r_cmap = plt.get_cmap('Reds')
        # g_cmap = plt.get_cmap('Blues')
        # b_cmap = plt.get_cmap('Gr')
        sctt = ax.scatter3D(numpy.log(x) if disp["log"]["x"] else x,
                            numpy.log(y) if disp["log"]["y"] else y,
                            numpy.log(z) if disp["log"]["z"] else z,
                            c=c, cmap=r_cmap)
        fig.colorbar(sctt, ax=ax, shrink=0.5, aspect=5)
    else:
        ax.scatter3D(numpy.log(x) if disp["log"]["x"] else x,
                     numpy.log(y) if disp["log"]["y"] else y,
                     numpy.log(z) if disp["log"]["y"] else z)
else:
    if "c" in disp.keys():
        r_cmap = plt.get_cmap('Reds')
        sctt = ax.scatter(numpy.log(x) if disp["log"]["x"] else x,
                          numpy.log(y) if disp["log"]["y"] else y,
                          c=c, cmap=r_cmap)
        fig.colorbar(sctt, ax=ax, shrink=0.5, aspect=5, label=disp["c"])
    else:
        ax.scatter(numpy.log(x) if disp["log"]["x"] else x,
                   numpy.log(y) if disp["log"]["y"] else y)

ax.set_xlabel(disp["x"])
ax.set_ylabel(disp["y"])
if "z" in disp.keys():
    ax.set_zlabel(disp["z"])

plt.show()