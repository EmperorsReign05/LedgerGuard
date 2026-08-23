import json
import random
import uuid
import argparse
from datetime import datetime, timedelta, timezone

def generate_id(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

def generate_clean_case(time_offset):
    p_id = generate_id("P-")
    s_id = generate_id("S-")
    utr = generate_id("UTR-")
    
    amount = random.randint(10000, 50000) # e.g. 100.00 to 500.00
    fee = int(amount * 0.02)
    tax = int(fee * 0.18)
    settled_amount = amount - fee - tax

    p_time = datetime.now(timezone.utc) - timedelta(days=time_offset)
    s_time = p_time + timedelta(days=random.randint(1, 3))

    payment = {
        "id": p_id,
        "amount": amount,
        "currency": "INR",
        "status": "captured",
        "captured_at": p_time.isoformat(),
        "metadata": {"type": "regular"}
    }
    
    settlement = {
        "id": s_id,
        "amount": settled_amount,
        "fees": fee,
        "tax": tax,
        "utr": utr,
        "status": "processed",
        "settled_at": s_time.isoformat(),
        "payment_references": [p_id]
    }

    ground_truth = {
        "case_id": generate_id("CASE-"),
        "records": [p_id, s_id],
        "expected_status": "EXACT_MATCH",
        "expected_match": [p_id, s_id],
        "expected_root_cause": "NONE",
        "expected_action": "AUTO_RESOLVE"
    }
    
    return [payment], [settlement], [], ground_truth

def generate_missing_utr_case(time_offset):
    payments, settlements, refunds, gt = generate_clean_case(time_offset)
    settlements[0]["utr"] = None
    
    gt["expected_status"] = "CANDIDATE_MATCH"
    gt["expected_root_cause"] = "MISSING_UTR"
    gt["expected_action"] = "REVIEW"
    
    return payments, settlements, refunds, gt

def generate_amount_mismatch_case(time_offset):
    payments, settlements, refunds, gt = generate_clean_case(time_offset)
    # Inject a random discrepancy (e.g. system bug didn't deduct tax correctly)
    settlements[0]["amount"] += random.choice([-500, 500])
    
    gt["expected_status"] = "EXCEPTION"
    gt["expected_root_cause"] = "AMOUNT_MISMATCH"
    gt["expected_action"] = "ESCALATE"
    
    return payments, settlements, refunds, gt

def generate_delayed_settlement_case(time_offset):
    payments, settlements, refunds, gt = generate_clean_case(time_offset)
    p_time = datetime.fromisoformat(payments[0]["captured_at"])
    # Delayed by 15 days
    s_time = p_time + timedelta(days=15)
    settlements[0]["settled_at"] = s_time.isoformat()
    
    gt["expected_status"] = "CANDIDATE_MATCH"
    gt["expected_root_cause"] = "TIMESTAMP_DRIFT"
    gt["expected_action"] = "AUTO_RESOLVE"
    
    return payments, settlements, refunds, gt

def generate_dataset(count, seed, anomaly_rates):
    random.seed(seed)
    
    all_payments = []
    all_settlements = []
    all_refunds = []
    ground_truths = []
    
    for i in range(count):
        r = random.random()
        time_offset = random.randint(1, 30)
        
        if r < anomaly_rates.get("missing_utr", 0.05):
            p, s, ref, gt = generate_missing_utr_case(time_offset)
        elif r < anomaly_rates.get("missing_utr", 0.05) + anomaly_rates.get("amount_mismatch", 0.05):
            p, s, ref, gt = generate_amount_mismatch_case(time_offset)
        elif r < anomaly_rates.get("missing_utr", 0.05) + anomaly_rates.get("amount_mismatch", 0.05) + anomaly_rates.get("delayed_settlement", 0.05):
            p, s, ref, gt = generate_delayed_settlement_case(time_offset)
        else:
            p, s, ref, gt = generate_clean_case(time_offset)
            
        all_payments.extend(p)
        all_settlements.extend(s)
        all_refunds.extend(ref)
        ground_truths.append(gt)

    # Shuffle to simulate real-world chaotic incoming data
    random.shuffle(all_payments)
    random.shuffle(all_settlements)
    
    return {
        "payments": all_payments,
        "settlements": all_settlements,
        "refunds": all_refunds
    }, ground_truths

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic financial dataset.")
    parser.add_argument("--count", type=int, default=100, help="Number of cases to generate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()
    
    rates = {
        "missing_utr": 0.05,
        "amount_mismatch": 0.05,
        "delayed_settlement": 0.05
    }
    
    dataset, gt = generate_dataset(args.count, args.seed, rates)
    
    dataset_path = f"data/generated/dataset_{args.seed}_{args.count}.json"
    gt_path = f"data/ground_truth/ground_truth_{args.seed}_{args.count}.json"
    
    with open(dataset_path, "w") as f:
        json.dump(dataset, f, indent=2)
        
    with open(gt_path, "w") as f:
        json.dump(gt, f, indent=2)
        
    print(f"Generated {args.count} cases.")
    print(f"Dataset saved to {dataset_path}")
    print(f"Ground truth saved to {gt_path}")
