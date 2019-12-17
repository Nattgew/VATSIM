
<?php

function cmp(array $a, array $b) {
    if ($a['frq'] < $b['frq']) {
        return -1;
    } else if ($a['frq'] > $b['frq']) {
        return 1;
    } else {
        return 0;
    }
}

function readalt(string $altstr) {
    if (substr($altstr,0,2) == "FL") {
        $alt = substr($altstr,3);
    } else {
        try {
            $alt = int($altstr);
        } catch (Exception $e) {
            echo "Could not determine altitude: ".$altstr;
            $alt = 0;
        }
    }
}

// Get these from POST
$departure = sys.argv[1];
$arrival = sys.argv[2];

// TODO: Some sort of validation on this
$fps = getfplist($departure, $arrival);

// Route, min alt, max alt, total
$routes = array();

foreach ($fps as &$fp) {
    if (count($routes) == 0) {
        $routes[] = array('route' => $fp['planned_route'], 'minalt' => $fp['planned_altitude'], 'maxalt' => $fp['planned_altitude'], 'frq' => 1);
    } else {
        for ($i = 0; $i < count($routes); $i++) {
            if ( $fp['planned_route'] == $routes[$i]['route'] ) {
                $routes[$i]['frq']++;
                // Track max/min altitudes
                // May need to type as int
                if ($fp['planned_altitude'] < $routes[$i]['minalt'] ) {
                    $routes[$i]['minalt'] = $fp['planned_altitude'];
                } elseif ( $fp['planned_altitude'] > $routes[$i]['maxalt']) {
                    $routes[$i]['maxalt'] = $fp['planned_altitude'];
                }
            }
        }
    }
}
usort($routes, 'cmp');
?>
<table><tr><th>Freq</th><th>Altitudes</th><th>Route</th></tr>
<?php
foreach ($routes as &$rt) {
    echo "<tr><td>".$rt['frq']."</td><td>FL".substr($rt['minalt'],0,3)."-FL".substr($rt['maxalt'],0,3)."</td><td>".$rt['route'])."</td></tr>";
}
?>
</table>
