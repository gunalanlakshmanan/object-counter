import os

from counter.domain.ports import ObjectCountRepo, ObjectDetector
from counter.adapters.count_repo import CountInMemoryRepo, CountMongoDBRepo, CountSQLRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects, DetectObjects


def get_count_adapter() -> ObjectCountRepo:
    db_type = os.environ.get('DB_TYPE', 'MongoDB')
    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', 27017)
    db = os.environ.get('DB_NAME', 'prod_counter')
    user = os.environ.get('DB_USER', 'postgres')
    pswd = os.environ.get('DB_PSWD', 'postgres')

    count_repo = f"Count{db_type}Repo"
    return globals()[count_repo](host=host, port=port, database=db, user=user, pswd=pswd)


def get_object_detector() -> ObjectDetector:
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    return TFSObjectDetector(tfs_host, tfs_port, 'rfcn')


# ================
# Count Action
# ================


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), CountInMemoryRepo())


def prod_count_action() -> CountDetectedObjects:
    object_detector = get_object_detector()
    count_adapter = get_count_adapter()
    return CountDetectedObjects(object_detector, count_adapter)


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()


# ================
# Detect Action
# ================

def dev_detect_action() -> DetectObjects:
    return DetectObjects(FakeObjectDetector())


def prod_detect_action() -> DetectObjects:
    object_detector = get_object_detector()
    return DetectObjects(object_detector)


def get_detect_action() -> DetectObjects:
    env = os.environ.get('ENV', 'dev')
    detect_action_fn = f"{env}_detect_action"
    return globals()[detect_action_fn]()
