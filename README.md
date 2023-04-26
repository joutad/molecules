# molecules
web app that reads SDF files and generates an SVG of the molecule


## installation
clone/pull the repo and then run "make". then make sure to run the following commands:

`export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.`

`chmod 755 libmol.so`

Finally, enter this command with `<port>` being a port number of your choosing:

`python3 server.py <port>`

Open a browser and go to the address `localhost:<port>`. You should be redirected to the index page, where you can add or remove elements.

For the 'upload' section, search for an sdf file for a molecule (ex. Water), and upload that sdf in the upload section.

The 'select' section allows you to select which molecule will be displayed. To select, click on the molecule that you want selected.

The 'display' section should show the molecule as an svg image.

Feel free to mess around!

![Isopentanol](https://user-images.githubusercontent.com/72181663/234476119-59ad9897-f0a7-482b-9fcd-c1afe548bbc8.svg)
Image of isopentanol
