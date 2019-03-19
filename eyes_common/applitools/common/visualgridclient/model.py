import attr

from applitools.common.utils import general_utils


@attr.s
class RenderingInfo(object):
    service_url = attr.ib()
    access_token = attr.ib()
    results_url = attr.ib()


@attr.s
class RGridResource(object):
    url = attr.ib()
    content_type = attr.ib()
    content = attr.ib()
    _sha256 = attr.ib(init=False)

    @property
    def sha256(self):
        if not self._sha256:
            self._sha256 = general_utils.get_sha256_hash(self.content)
        return self._sha256


@attr.s
class RenderRequest(object):
    render_id = attr.ib()
    task = attr.ib()
    webhook = attr.ib()
    url = attr.ib()
    dom = attr.ib()
    resources = attr.ib()
    render_info = attr.ib()
    platform = attr.ib()
    browser_name = attr.ib()
    script_hooks = attr.ib()
    selectors_to_find_regions_for = attr.ib()
    send_dom = attr.ib()


@attr.s
class RunningRender(object):
    render_id = attr.ib()
    job_id = attr.ib()
    render_status = attr.ib()
    need_more_resources = attr.ib()
    need_more_dom = attr.ib()
