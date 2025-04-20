from commons.base.constants import BaseConstant

class TripletType(BaseConstant):
    DIRECT_CONTINUE = "DIRECT_CONTINUE"
    BRIDGE_AND_CONTINUE = "BRIDGE_AND_CONTINUE"
    NEEDS_INPUT = "NEEDS_INPUT"
    INVALID_USER_INPUT = "INVALID_USER_INPUT"

# Directory names for triplet files
GENERATED_TRIPLETS_DIR = "generated_triplets"
EVELUATED_TRIPLETS_DIR = "evaluated_triplets" 