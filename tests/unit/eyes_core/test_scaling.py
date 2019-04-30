from applitools.core import ContextBasedScaleProvider


# TODO: check correctness of calculation
def test_contextbasedscaleprovider_desktop():
    cbsp = ContextBasedScaleProvider(
        {"width": 1200, "height": 1600},
        viewport_size={"width": 800, "height": 400},
        device_pixel_ratio=3.43,
        is_mobile_device=False,
    )
    cbsp.update_scale_ratio(400)
    assert cbsp.scale_ratio


def test_contextbasedscaleprovider_mobile():
    cbsp = ContextBasedScaleProvider(
        {"width": 1200, "height": 1600},
        viewport_size={"width": 800, "height": 400},
        device_pixel_ratio=3.43,
        is_mobile_device=True,
    )
    cbsp.update_scale_ratio(400)
    assert cbsp.scale_ratio
