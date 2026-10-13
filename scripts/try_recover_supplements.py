#!/usr/bin/env python3
"""Attempt journal-hosted supplement recovery on CI runner.

No copyrighted PDF/text is committed or uploaded as an artifact.
Outputs: URL/status, PDF signature/hash, page count, and concise evidence
that target tables can be located. NO scientific approval or label export.
"""
from __future__ import annotations
import hashlib
import io
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

SOURCES={
"Li2026_RSC_SI":[
"https://www.rsc.org/suppdata/d6/em/d6em00059b/d6em00059b1.pdf",
"https://pubs.rsc.org/en/content/supplementary/d6em00059b"],
"Yuan2023_ACS_SI":[
"https://pubs.acs.org/doi/suppl/10.1021/acs.jafc.2c08748/suppl_file/jf2c08748_si_001.pdf",
"https://acs.figshare.com/doi/suppl/10.1021/acs.jafc.2c08748"]
}
UA="Mozilla/5.0 (compatible; TransHazard-Research-Supplement-Recovery/1.0)"
results={}
for key,urls in SOURCES.items():
    info={"status":"NOT_RETRIEVED","attempts":[]}
    for url in urls:
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":UA,
                "Accept":"application/pdf,text/html;q=0.5,*/*;q=0.1",
            })
            with urllib.request.urlopen(req,timeout=25) as h:
                data=h.read(4_000_000)
                mime=h.headers.get("Content-Type","")
                final=h.geturl()
                item={"source":url,"resolved_url":final,"http":h.status,"mime":mime,"bytes_read":len(data)}
            if data[:5]!=b"%PDF-":
                item["failure"]="CONTENT_NOT_A_PDF"
                info["attempts"].append(item)
                continue
            item["sha256"]=hashlib.sha256(data).hexdigest()
            try:
                from pypdf import PdfReader
                p=PdfReader(io.BytesIO(data))
                item["pdf_pages"]=len(p.pages)
                matches=[]
                for i,page in enumerate(p.pages):
                    txt=page.extract_text() or ""
                    for token in (["LC50","LC 50","X11519540","X11719474","Table S2"] if key.startswith("Yuan")
                                  else ["LC50","HHCB-lac","HHCB lactone","Table S"]):
                        if token.lower() in txt.lower():
                            matches.append({"page":i+1,"term":token})
                item["keyword_page_matches"]=matches[:25]
                item["note"]="Retrieved PDF verified. No table value inferred without full human source inspection."
            except Exception as e:
                item["parse_warning"]=type(e).__name__
            info["status"]="PDF_RECOVERED_ON_CI_RUNNER_NOT_REDISTRIBUTED"
            info["attempts"].append(item)
            break
        except Exception as e:
            info["attempts"].append({"source":url,"error_type":type(e).__name__,
                                     "error_message":str(e)[:160]})
    results[key]=info
print(json.dumps(results,indent=2))
# Return success even for publisher anti-bot errors: scientific release remains NO-GO.
