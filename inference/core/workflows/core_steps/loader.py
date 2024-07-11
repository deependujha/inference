from typing import Callable, List, Tuple, Type, Union

from inference.core.cache import cache
from inference.core.env import API_KEY, WORKFLOWS_STEP_EXECUTION_MODE
from inference.core.workflows.core_steps.common.entities import StepExecutionMode
from inference.core.workflows.core_steps.flow_control.continue_if import ContinueIfBlock
from inference.core.workflows.core_steps.fusion.detections_consensus import (
    DetectionsConsensusBlock,
)
from inference.core.workflows.core_steps.models.foundation.clip_comparison import (
    ClipComparisonBlock,
)
from inference.core.workflows.core_steps.models.foundation.lmm import LMMBlock
from inference.core.workflows.core_steps.models.foundation.lmm_classifier import (
    LMMForClassificationBlock,
)
from inference.core.workflows.core_steps.models.foundation.ocr import OCRModelBlock
from inference.core.workflows.core_steps.models.foundation.yolo_world import (
    YoloWorldModelBlock,
)
from inference.core.workflows.core_steps.models.roboflow.instance_segmentation import (
    RoboflowInstanceSegmentationModelBlock,
)
from inference.core.workflows.core_steps.models.roboflow.keypoint_detection import (
    RoboflowKeypointDetectionModelBlock,
)
from inference.core.workflows.core_steps.models.roboflow.multi_class_classification import (
    RoboflowClassificationModelBlock,
)
from inference.core.workflows.core_steps.models.roboflow.multi_label_classification import (
    RoboflowMultiLabelClassificationModelBlock,
)
from inference.core.workflows.core_steps.models.roboflow.object_detection import (
    RoboflowObjectDetectionModelBlock,
)
from inference.core.workflows.core_steps.models.third_party.barcode_detection import (
    BarcodeDetectorBlock,
)
from inference.core.workflows.core_steps.models.third_party.qr_code_detection import (
    QRCodeDetectorBlock,
)
from inference.core.workflows.core_steps.sinks.roboflow.roboflow_dataset_upload import (
    RoboflowDatasetUploadBlock,
)
from inference.core.workflows.core_steps.transformations.absolute_static_crop import (
    AbsoluteStaticCropBlock,
)
from inference.core.workflows.core_steps.transformations.detection_offset import (
    DetectionOffsetBlock,
)
from inference.core.workflows.core_steps.transformations.detections_filter import (
    DetectionsFilterBlock,
)
from inference.core.workflows.core_steps.transformations.detections_transformation import (
    DetectionsTransformationBlock,
)
from inference.core.workflows.core_steps.transformations.dynamic_crop import (
    DynamicCropBlock,
)
from inference.core.workflows.core_steps.transformations.dynamic_zones import (
    DynamicZonesBlock,
)
from inference.core.workflows.core_steps.transformations.perspective_correction import (
    PerspectiveCorrectionBlock,
)
from inference.core.workflows.core_steps.transformations.relative_static_crop import (
    RelativeStaticCropBlock,
)
from inference.core.workflows.entities.types import Kind, WILDCARD_KIND, IMAGE_KIND, BATCH_OF_IMAGES_KIND, \
    ROBOFLOW_MODEL_ID_KIND, ROBOFLOW_PROJECT_KIND, ROBOFLOW_API_KEY_KIND, FLOAT_ZERO_TO_ONE_KIND, LIST_OF_VALUES_KIND, \
    BATCH_OF_SERIALISED_PAYLOADS_KIND, BOOLEAN_KIND, BATCH_OF_BOOLEAN_KIND, INTEGER_KIND, STRING_KIND, \
    BATCH_OF_STRING_KIND, BATCH_OF_TOP_CLASS_KIND, FLOAT_KIND, DICTIONARY_KIND, BATCH_OF_DICTIONARY_KIND, \
    BATCH_OF_CLASSIFICATION_PREDICTION_KIND, DETECTION_KIND, POINT_KIND, ZONE_KIND, OBJECT_DETECTION_PREDICTION_KIND, \
    BATCH_OF_OBJECT_DETECTION_PREDICTION_KIND, INSTANCE_SEGMENTATION_PREDICTION_KIND, \
    BATCH_OF_INSTANCE_SEGMENTATION_PREDICTION_KIND, KEYPOINT_DETECTION_PREDICTION_KIND, \
    BATCH_OF_KEYPOINT_DETECTION_PREDICTION_KIND, BATCH_OF_QR_CODE_DETECTION_KIND, BATCH_OF_BAR_CODE_DETECTION_KIND, \
    BATCH_OF_PREDICTION_TYPE_KIND, BATCH_OF_PARENT_ID_KIND, BATCH_OF_IMAGE_METADATA_KIND
from inference.core.workflows.prototypes.block import (
    WorkflowBlock,
    WorkflowBlockManifest,
)

REGISTERED_INITIALIZERS = {
    "api_key": lambda: API_KEY,
    "cache": cache,
    "step_execution_mode": StepExecutionMode(WORKFLOWS_STEP_EXECUTION_MODE),
}


def load_blocks() -> List[
    Union[
        Type[WorkflowBlock],
        Tuple[
            Type[WorkflowBlockManifest],
            Callable[[Type[WorkflowBlockManifest]], WorkflowBlock],
        ],
    ]
]:
    return [
        DetectionsConsensusBlock,
        ClipComparisonBlock,
        LMMBlock,
        LMMForClassificationBlock,
        OCRModelBlock,
        YoloWorldModelBlock,
        RoboflowInstanceSegmentationModelBlock,
        RoboflowKeypointDetectionModelBlock,
        RoboflowClassificationModelBlock,
        RoboflowMultiLabelClassificationModelBlock,
        RoboflowObjectDetectionModelBlock,
        BarcodeDetectorBlock,
        QRCodeDetectorBlock,
        AbsoluteStaticCropBlock,
        DynamicCropBlock,
        DetectionsFilterBlock,
        DetectionOffsetBlock,
        RelativeStaticCropBlock,
        DetectionsTransformationBlock,
        RoboflowDatasetUploadBlock,
        ContinueIfBlock,
        PerspectiveCorrectionBlock,
        DynamicZonesBlock,
    ]


def load_kinds() -> List[Kind]:
    return [
        WILDCARD_KIND,
        IMAGE_KIND,
        BATCH_OF_IMAGES_KIND,
        ROBOFLOW_MODEL_ID_KIND,
        ROBOFLOW_PROJECT_KIND,
        ROBOFLOW_API_KEY_KIND,
        FLOAT_ZERO_TO_ONE_KIND,
        LIST_OF_VALUES_KIND,
        BATCH_OF_SERIALISED_PAYLOADS_KIND,
        BOOLEAN_KIND,
        BATCH_OF_BOOLEAN_KIND,
        INTEGER_KIND,
        STRING_KIND,
        BATCH_OF_STRING_KIND,
        BATCH_OF_TOP_CLASS_KIND,
        FLOAT_KIND,
        DICTIONARY_KIND,
        BATCH_OF_DICTIONARY_KIND,
        BATCH_OF_CLASSIFICATION_PREDICTION_KIND,
        DETECTION_KIND,
        POINT_KIND,
        ZONE_KIND,
        OBJECT_DETECTION_PREDICTION_KIND,
        BATCH_OF_OBJECT_DETECTION_PREDICTION_KIND,
        INSTANCE_SEGMENTATION_PREDICTION_KIND,
        BATCH_OF_INSTANCE_SEGMENTATION_PREDICTION_KIND,
        KEYPOINT_DETECTION_PREDICTION_KIND,
        BATCH_OF_KEYPOINT_DETECTION_PREDICTION_KIND,
        BATCH_OF_QR_CODE_DETECTION_KIND,
        BATCH_OF_BAR_CODE_DETECTION_KIND,
        BATCH_OF_PREDICTION_TYPE_KIND,
        BATCH_OF_PARENT_ID_KIND,
        BATCH_OF_IMAGE_METADATA_KIND,
    ]
