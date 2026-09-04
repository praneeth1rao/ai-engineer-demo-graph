from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

def main():
    styles=getSampleStyleSheet(); doc=SimpleDocTemplate('architecture.pdf',pagesize=A4,rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36)
    story=[Paragraph('AI Intelligence Graph — Architecture',styles['Title']),Spacer(1,12)]
    story += [Paragraph('1. Ingestion',styles['Heading2']),Paragraph('Public startup/product listings, arXiv research, RSS news, and public job JSON endpoints are collected with bounded timeouts. Source URLs are retained for traceability.',styles['BodyText']),Spacer(1,8)]
    story += [Paragraph('2. Reliability',styles['Heading2']),Paragraph('HTTP failures are isolated per source. LLM calls use provider fallback, exponential backoff with jitter for HTTP 429, and smaller chunks after HTTP 413.',styles['BodyText']),Spacer(1,8)]
    story += [Paragraph('3. Freshness',styles['Heading2']),Paragraph('News and jobs are admitted only when their source timestamp falls within the exact 24-hour window (with a small future clock-skew allowance). Missing timestamps are rejected.',styles['BodyText']),Spacer(1,8)]
    story += [Paragraph('4. Entity resolution',styles['Heading2']),Paragraph('Names are normalized and compared deterministically against a 50-record seed list using similarity scoring. Every mapping retains the source URL.',styles['BodyText']),Spacer(1,8)]
    story += [Paragraph('5. Storage',styles['Heading2']),Paragraph('CSV files are Google-Sheet-ready; an XLSX workbook contains the six required tabs. A production deployment can move raw documents to object storage, primary records to PostgreSQL, vectors to a vector index, and relationships to a graph database.',styles['BodyText']),Spacer(1,8)]
    data=[['Layer','Demo implementation','Production direction'],['Sources','HTTP/RSS/JSON','Async workers + queue'],['Primary records','CSV/XLSX','PostgreSQL'],['Vectors','Not required for demo','Vector DB'],['Relationships','Entity Mapping Log','Graph DB'],['Observability','Console diagnostics','Metrics/traces/alerts']]
    t=Table(data,colWidths=[90,190,220]); t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.lightgrey),('VALIGN',(0,0),(-1,-1),'TOP')]))
    story += [t]; doc.build(story)
if __name__=='__main__': main()
