from __future__ import print_function

import logging
import yaml

import numpy as np
import orca
import pandas as pd

from . import misc
from ..models import util

logger = logging.getLogger(__name__)


def from_yaml(net, cfgname):
    print("Computing accessibility variables")
    cfg = yaml.load(open(misc.config(cfgname)))

    nodes = pd.DataFrame(index=net.node_ids)

    assert "node_col" in cfg, "Need to specify from where to take the node id"
    node_col = cfg.get('node_col')

    for variable in cfg['variable_definitions']:

        name = variable["name"]
        print("Computing %s" % name)

        decay = variable.get("decay", "linear")
        agg = variable.get("aggregation", "sum")
        if agg == "aggregation":
            agg = 'ave'
        vname = variable.get("varname", None)
        radius = float(variable["radius"])
        dfname = variable["dataframe"]

        flds = [vname] if vname else []
        flds.append(node_col)
        if "filters" in variable:
            flds += util.columns_in_filters(variable["filters"])
        logger.info("    Fields available to aggregate = " + ', '.join(flds))

        df = orca.get_table(dfname).to_frame(flds)

        if "filters" in variable:
            df = util.apply_filter_query(df, variable["filters"])
            logger.info("    Filters = %s" % variable["filters"])

        logger.info("    dataframe = %s, varname=%s" % (dfname, vname))
        logger.info("    radius = %s, aggregation = %s, decay = %s" % (
            radius, agg, decay))

        # set the variable
        net.set(df[node_col], variable=df[vname].astype(float) if vname else None)
        # aggregate it
        nodes[name] = net.aggregate(radius, type=agg, decay=decay)

        if "apply" in variable:
            nodes[name] = nodes[name].apply(eval(variable["apply"]))

    return nodes
