import argparse

from true_positive.correlate import correlate
from true_positive.ingest import load_findings
from true_positive.scoring import score_incident


def main():
    parser = argparse.ArgumentParser(description="True Positive triage pipeline")
    parser.add_argument("--source", default="data/sample_findings.json")
    args = parser.parse_args()
    findings = load_findings(args.source)
    by_id = {f.id: f for f in findings}
    incidents = correlate(findings)
    for incident in incidents:
        score_incident(incident, by_id)
    incidents.sort(key=lambda i: i.score, reverse=True)
    print("%d findings -> %d incidents\n" % (len(findings), len(incidents)))
    for incident in incidents:
        print("%s  score %.1f  findings: %s" % (
            incident.id, incident.score, ", ".join(incident.finding_ids)))
        for reason in incident.score_reasons:
            print("    - %s" % reason)
        print()


if __name__ == "__main__":
    main()
