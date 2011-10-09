from models import TestReview, TestReviewSegment
from forms import TestReviewForm, TestReviewSegmentForm

def get_model():
    return TestReview

def get_segment_model():
    return TestReviewSegment

def get_form():
    return TestReviewForm

def get_segment_form():
    return TestReviewSegmentForm