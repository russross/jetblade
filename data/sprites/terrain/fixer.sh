find . -name "*png" | perl -ne 'chomp; `convert -resize 37% -crop 100x100+0+0\! -gravity center $_ $_`'
