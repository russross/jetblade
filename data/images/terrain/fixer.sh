mv 0001.png center.png
mv 0002.png upleft.png
mv 0003.png up.png
mv 0004.png upright.png
mv 0005.png right.png
mv 0006.png downright.png
mv 0007.png down.png
mv 0008.png downleft.png
mv 0009.png left.png
mv 0010.png leftright.png
mv 0011.png upleftsquare.png
mv 0012.png updown.png
mv 0013.png uprightsquare.png
mv 0014.png allway.png
mv 0015.png downrightsquare.png
mv 0016.png downleftsquare.png
mv 0017.png leftend.png
mv 0018.png upend.png
mv 0019.png rightend.png
mv 0020.png downend.png
ls | perl -ne 'chomp; `convert -crop 340x340+230+130 $_ $_`'
ls | perl -ne 'chomp; `convert -resize 22.73% $_ $_`'
