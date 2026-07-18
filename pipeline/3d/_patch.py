# Import this FIRST: makes missing/empty linetypes non-fatal (preview only)
import ezdxf.entities.dxfgfx as _dg
from ezdxf.lldxf import const as _const
_orig=_dg.DXFGraphic.post_new_hook
def _safe(self):
    try: _orig(self)
    except _const.DXFInvalidLineType:
        try: self.dxf.linetype="BYLAYER"
        except Exception: pass
_dg.DXFGraphic.post_new_hook=_safe
