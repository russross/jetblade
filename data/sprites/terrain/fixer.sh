find . -name "*png" | perl -ne 'chomp; `convert -resize 37% -crop 77x77+0+0\! -gravity center $_ $_`'
