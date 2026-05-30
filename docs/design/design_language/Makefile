design_language_conjectures.v0.html: design_language_conjectures_build.md _conjectures_header.html references.bib apa.csl
	pandoc design_language_conjectures_build.md \
		--standalone \
		--embed-resources \
		--filter mermaid-filter \
		--citeproc \
		--include-in-header _conjectures_header.html \
		--metadata title="Conjecture Mapping Unfold Studio's Design Language" \
		--from markdown+raw_html \
		--to html5 \
		-o $@

.PHONY: clean open
clean:
	rm -f design_language_conjectures.v0.html
open: design_language_conjectures.v0.html
	open $<
