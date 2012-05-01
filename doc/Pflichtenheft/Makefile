FILE=TemplatePflichtenheft

default:
	pdflatex  -interaction=nonstopmode ${FILE}
	makeindex -s ${FILE}.ist -t ${FILE}.alg -o ${FILE}.acr ${FILE}.acn
	makeindex -s ${FILE}.ist -t ${FILE}.glg -o ${FILE}.gls ${FILE}.glo
	pdflatex -interaction=nonstopmode ${FILE}
	pdflatex -interaction=nonstopmode ${FILE}
	pdflatex -interaction=nonstopmode ${FILE}

clean:
	find . -name '*.aux' -delete
	find . -name '*.ist' -delete
	find . -name '*.gls' -delete
	find . -name '*.lof' -delete
	find . -name '*.log' -delete
	find . -name '*.toc' -delete
	find . -name '*.acn' -delete
	find . -name '*.out' -delete
	find . -name '*.glo' -delete
	find . -name '*.acr' -delete
	find . -name '*.glg' -delete
	find . -name '*.alg' -delete
