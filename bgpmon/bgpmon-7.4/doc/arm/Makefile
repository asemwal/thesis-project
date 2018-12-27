
DOC=arm
PDFLATEX=pdflatex
BIBTEX=bibtex
DVIPS=dvips
PS2PDF=ps2pdf
ALLTEX=$(wildcard *.tex)
REDUCE=psnup -n 2

all: arm.pdf quickstart.pdf

spelling: 
	ispell -t $(ALLTEX)

clean:
	rm -f *.tex.bak arm.dvi arm.aux *.aux arm.log arm.bbl arm.blg \
	arm.ps arm.pdf \
	arm.lot arm.lof arm.toc \
	rm -f *.tex.bak quickstart.dvi quickstart.aux *.aux quickstart.log quickstart.bbl quickstart.blg \
	quickstart.ps quickstart.pdf \
	quickstart.lot quickstart.lof quickstart.toc 
	
arm.ps: arm.dvi
	$(DVIPS) arm.dvi -Ppdf -t letter -o arm.ps

quickstart.pdf: quickstart.tex
	$(PDFLATEX) quickstart.tex;$(BIBTEX) quickstart;$(PDFLATEX) quickstart;$(PDFLATEX) quickstart

arm.pdf: $(ALLTEX)
	$(PDFLATEX) arm.tex;$(BIBTEX) arm;$(PDFLATEX) arm;$(PDFLATEX) arm

arm.2.ps: arm.ps
	$(REDUCE) arm.ps > arm.2.ps

