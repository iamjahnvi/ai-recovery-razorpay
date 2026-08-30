import random

# The policy says "retry". Now simulate what actually happens when we attempt that retry.

def stimulate_retry(payment):
    failure_reason = payment["failure_reason"]

    if failure_reason in {"incorrect_CVC", "mismatched_card_number", "expired_card"}:
        return{
            "success" : False,
            "result" : "retry_failed",
            "reason":"Payment details must be updated by the customer."
        }

    if failure_reason == "insufficient_funds":
        return{
            "success": False,
        }

    if failure_reason == "processing_error":
        success =  random.random() < 0.70 

        if success:
            return{
                "success":True,
                "result":"recovered" ,
                "reason":"Transient processing issue resolved."
            }

        return{
            "success":False,
            "result":"retry_failed" ,
            "reason":"Processing issue still persisting"
        }

    if failure_reason == "bank_declined":
        success = random.random() < 0.40

        if success :
            return{
                "success":True,
                "result":"recovered" ,
                "reason":"Bank declined issue resolved."
            }

        return{
            "success":False,
            "result":"retry_failed" ,
            "reason":"Bank declination still persists"
        }