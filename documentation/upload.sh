make html
make latexpdf
cp _build/latex/UnfoldStudio.pdf _build/html/
rsync -r _build/html/* zdcp@chrisproctor.net:/home/zdcp/public_html/docs.unfold.studio/
