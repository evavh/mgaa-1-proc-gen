#!/bin/bash

#SUCCESS=false

#ls $1.tex | entr -rc bash -c "mv $1.aux $1.aux.back; pdflatex -shell-escape -halt-on-error $1 && ./open_once.sh $1 $SUCCESS && SUCCESS=true"
ls $1.tex | entr -rc bash -c "mv $1.aux $1.aux.back; pdflatex -shell-escape -halt-on-error $1; biber $1; pdflatex $1"
