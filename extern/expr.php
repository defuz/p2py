<?php

abstract class CommandBuilderBase extends LCachableComponent {

    protected abstract function getMainTable();

    protected abstract function getTablePrefix();

    protected abstract function getSelect();

    protected abstract function getFrom();

    protected abstract function getMicrodistrictCondition($microdistricts);

    protected abstract function getSubwayCondition($subwayStations, $distance);

    protected function getIndexes() {
        return '';
    }

    protected function getSelectPrefix() {
        return isset($_GET['nocache']) ? 'SELECT SQL_NO_CACHE' : 'SELECT ';
    }

    public function limitPrice($parameters) {
        if (isset($parameters['city'])
         && isset($parameters['realtyType'])
         && isset($parameters['contractType'])) {

            $prices = City::factory()->findById($parameters['city'])->getPriceLimit($parameters['contractType'], $parameters['realtyType']);
            if ((!isset($parameters['priceMin']) || empty($parameters['priceMin'])) && isset($prices['priceMin'])) {
                $parameters['currencyMin'] = $prices['currency'];
                $parameters['priceMin'] = $prices['priceMin'];
            }
            if ((!isset($parameters['priceMax']) || empty($parameters['priceMax'])) && isset($prices['priceMax'])) {
                $parameters['currencyMax'] = $prices['currency'];
                $parameters['priceMax'] = $prices['priceMax'];
            }
        }
        if (isset($parameters['currency'])) {
            if (!isset($parameters['currencyMin']))
                $parameters['currencyMin'] = $parameters['currency'];
            if (!isset($parameters['currencyMax']))
                $parameters['currencyMax'] = $parameters['currency'];
            unset($parameters['currency']);
        }
        return $parameters;
    }

    public function constructSelectSql($parameters, $view = null) {
        $this->parameters = $parameters;
        $sql = "{$this->selectPrefix} {$this->select},
                       a_locations.latitude, a_locations.longitude";
        if (!empty($view)) {
            $sql.= ', a_view_cache.data as view';
        }
        $sql .= ' ' . $this->from;
        if (!empty($parameters['phone']))
            $sql .= " INNER JOIN {$this->tablePrefix}_phones ON {$this->tablePrefix}_phones.group_id = a_p.group_id AND {$this->tablePrefix}_phones.phone = '8" . $parameters['phone'] . "' ";
        if (!empty($parameters['sites']))
            $sql .= " INNER JOIN {$this->tablePrefix}_urls ON a_p.group_id = {$this->tablePrefix}_urls.group_id AND {$this->tablePrefix}_urls.site = " . implode(', ', $parameters['sites']) . ' ';
        elseif (!empty($parameters['block']))
            $sql .= " LEFT JOIN {$this->tablePrefix}_urls ON a_p.group_id = {$this->tablePrefix}_urls.group_id AND {$this->tablePrefix}_urls.site IN (" . implode(', ', $parameters['block']) . ') ';
        if (isset($parameters['building'])) {
            $sql .= ' INNER JOIN n_street ON n_street.street_id = a_p.street AND n_street.house = a_p.house
                      INNER JOIN n_building ON n_street.n_id = n_building.n_id AND n_building.n_id = ' . $parameters['building'] . ' ';
        }
        if (!empty($view)) {
            $sql .= ' LEFT JOIN a_view_cache ON a_view_cache.group_id = a_p.group_id AND a_view_cache.view = "' . $view . '" ';
        }
        if (isset($parameters['contractType']) && $parameters['contractType'] == CONTRACT_TYPE_DAILY_RENT) {
            $sql .= ' LEFT JOIN a_daily_featured ON a_daily_featured.group_id = a_p.group_id ';
            $sql .= ' LEFT JOIN a_daily_hidden ON a_daily_hidden.group_id = a_p.group_id ';
        }
        $sql .= " LEFT JOIN a_locations ON a_locations.id = a_p.location_id {$this->constructWhere($parameters)}{$this->constructOrder($parameters)}";
        return $sql;
    }

    public function constructCountSql($parameters, $limit = null) {
        $this->parameters = $parameters;
        if (!empty($parameters['phone'])) {
            $phone_table = $this->tablePrefix . '_phones';
            $sql = "{$this->selectPrefix} COUNT({$phone_table}.group_id) AS count FROM {$phone_table} WHERE {$phone_table}.phone = '8{$parameters['phone']}'";
        } else {
            $sql = "{$this->selectPrefix} COUNT(*) AS count FROM {$this->mainTable} LEFT JOIN a_locations ON a_locations.id = a_p.location_id";

            if (isset($parameters['building'])) {
                $sql .= " INNER JOIN n_street ON n_street.street_id = a_p.street AND n_street.house = a_p.house
                          INNER JOIN n_building ON n_street.n_id = n_building.n_id AND n_building.n_id = " . $parameters['building'] . ' ';
            }

            if (!empty($parameters['sites']))
                $sql .= " INNER JOIN {$this->tablePrefix}_urls ON a_p.group_id = {$this->tablePrefix}_urls.group_id AND {$this->tablePrefix}_urls.site = " . implode(', ', $parameters['sites']) . ' ';
            elseif (!empty($parameters['block']))
                $sql .= " LEFT JOIN {$this->tablePrefix}_urls ON a_p.group_id = {$this->tablePrefix}_urls.group_id AND {$this->tablePrefix}_urls.site IN (" . implode(', ', $parameters['block']) . ') ';

            if (isset($parameters['contractType']) && $parameters['contractType'] == CONTRACT_TYPE_DAILY_RENT) {
                $sql .= ' LEFT JOIN a_daily_hidden ON a_daily_hidden.group_id = a_p.group_id ';
            }
            $sql .= $this->constructWhere($parameters);
        }
        if ($limit != null)
            $sql .= ' LIMIT ' . $limit;
        return $sql;
    }

    static $INTERVALS = array(
        'today' => 'INTERVAL  0 DAY',
        'yesterday' => 'INTERVAL  1 DAY',
        '3days' => 'INTERVAL  3 DAY',
        'week' => 'INTERVAL  7 DAY',
        '2weeks' => 'INTERVAL 14 DAY',
        'month' => 'INTERVAL  1 MONTH',
        '6months' => 'INTERVAL  6 MONTH',
    );

    static $CURRENCIES = array(
        CURRENCY_USD => 'usd',
        CURRENCY_UAH => 'uah',
        CURRENCY_EUR => 'eur',
    );

    protected function constructWhere($parameters, $filter_by_time = true) {
        $where = array();
        // groupId
        if (isset($parameters['groupId']))
            $where = array('a_p.group_id = ' . $parameters['groupId']);
        else {
            if ($filter_by_time) {
                // times
                if (isset($parameters['addTime'])) {
                    $value = $parameters['addTime'];
                    if (is_numeric($value))
                        $where[] = 'a_p.add_time >= "' . date('c', $value) . '"';
                    elseif ($value != 'all')
                        $where[] = 'a_p.add_time >= CURDATE() - ' . self::$INTERVALS[$value];
                    if (isset($parameters['addTimeDown']))
                        $where[] = 'a_p.add_time <= "' . date('c', $parameters['addTimeDown']) . '"';
                }
                elseif (isset($parameters['updateTime'])) {
                    $value = $parameters['updateTime'];
                    if (is_numeric($value))
                        $where[] = 'a_p.update_time >= "' . date('c', $value) . '"';
                    elseif ($value != 'all')
                        $where[] = 'a_p.update_time >= CURDATE() - ' . self::$INTERVALS[$value];
                }
            }
            // contract type
            if (isset($parameters['contractType']))
                $where[] = 'a_p.contract_type = ' . $parameters['contractType'];

            // realty type
            if (isset($parameters['realtyType']))
                $where[] = 'a_p.realty_type = ' . $parameters['realtyType'];

            // city
            if (isset($parameters['city']))
                $where[] = 'a_p.city = ' . $parameters['city'];

            if (isset($parameters['street'])) {
                // street
                $value = $parameters['street'];
                $where[] = '(a_p.street IN (' . implode(',', $value) . ') OR a_p.supstreet IN (' . implode(',', $value) . '))';
                // house
                if (isset($parameters['house']))
                    $where[] = 'a_p.house = "' . $parameters['house'] . '"';
            } else {

                if (isset($parameters['subway'])) {
                    $where[] = $this->getSubwayCondition($parameters['subway'], $parameters['distance']);
                } else {
                    $location = array();
                    // [micro]disctircts
                    if (isset($parameters['district'])) {
                        $value = $parameters['district'];
                        $location[] = is_array($value)
                                ? 'a_p.district IN (' . implode(',', $value) . ')'
                                : 'a_p.district = ' . $value;
                    }
                    if (isset($parameters['microdistrict'])) {
                        $location[] = $this->getMicrodistrictCondition($parameters['microdistrict']);
                    }

                    if ($location)
                        $where[] = '(' . implode(' OR ', $location) . ')';
                }
            }

//            if (isset($parameters['building'])) {
//                $where[] = 'a_p.building_id = ' . $parameters['building'] . ' ';
//            }


            // room count
            if (isset($parameters['roomCount']))
            {
                if ( !is_array( $parameters['roomCount'] ) )
                    $parameters['roomCount'] = array( $parameters['roomCount'] );
                $room = array();
                if ( in_array( '5', $parameters['roomCount'] ) )
                    $room[] = 'a_p.room_count > 5';

                $room[] = 'a_p.room_count IN (' . implode(',', $parameters['roomCount']) . ')';

                $where[] = '((' . implode( ') OR (', $room ) . '))';
            }

            // general Area
            if (isset($parameters['generalAreaMin']))
                $where[] = 'a_p.area_total >= ' . $parameters['generalAreaMin'];
            if (isset($parameters['generalAreaMax']))
                $where[] = 'a_p.area_total <= ' . $parameters['generalAreaMax'];

            // price
            if (isset($parameters['priceMin'])) {
                $currency_field = 'a_p.price_' . self::$CURRENCIES[$parameters['currencyMin']];
                $where[] = $currency_field . ' >= ' . $parameters['priceMin'];
            }
            if (isset($parameters['priceMax'])) {
                $currency_field = 'a_p.price_' . self::$CURRENCIES[$parameters['currencyMax']];
                $where[] = $currency_field . ' <= ' . $parameters['priceMax'];
            }

//            // envelope
//            if (isset($parameters['envelopeMinLat'])) {
//                $locations = Yii::app()->db->createCommand("SELECT id FROM a_locations
//                  WHERE a_locations.latitude  >= {$parameters['envelopeMinLat']}
//                    AND a_locations.latitude  <= {$parameters['envelopeMaxLat']}
//                    AND a_locations.longitude >= {$parameters['envelopeMinLng']}
//                    AND a_locations.longitude <= {$parameters['envelopeMaxLng']}
//                ")->queryColumn();
//                    $where[] = 'a_p.location_id IN ("' . implode('", "', $locations) . '")';
//            }

            // envelope
            if (isset($parameters['envelopeMinLat'])) {
                $where[] = "a_locations.latitude  >= {$parameters['envelopeMinLat']}
                        AND a_locations.latitude  <= {$parameters['envelopeMaxLat']}
                        AND a_locations.longitude >= {$parameters['envelopeMinLng']}
                        AND a_locations.longitude <= {$parameters['envelopeMaxLng']}";
            }

            // publisherId
            if (isset($parameters['publisher']))
                $where[] = 'a_p.publisher_id = ' . $parameters['publisher'];

            // checkboxes
            $without = array();

            if (!empty($parameters['withoutBrokers']))
                $without[] = 'a_p.publisher_id IN (' . PUBLISHER_OWNER . ', ' . PUBLISHER_PRESUMABLY_OWNER . ')';
            if (!empty($parameters['withoutFee']))
                $without[] = 'a_p.without_fee = "1"';

            if (!empty($without)) {
                $where[] = '(' . implode(' OR ', $without) . ')';
            }

            if (isset($parameters['newBuilding']) && $parameters['newBuilding'])
                $where[] = 'a_p.is_new_house = 1';
            if (isset($parameters['nearMetro']) && $parameters['nearMetro']) {
                $where[] = "EXISTS (SELECT * FROM a_locations_to_subway USE INDEX (near_metro) WHERE distance < 1000 AND a_p.location_id = a_locations_to_subway.location_id)";
            }
            if (isset($parameters['hasPhotos']))
                $where[] = 'a_p.has_images = 1';
            if (isset($parameters['premium']) && $parameters['premium'] == '1')
                $where[] = 'a_p.premium > 0';

            // block site
            if (!empty($parameters['block']))
                $where[] = $this->tablePrefix . '_urls.group_id IS NULL';

            if (isset($parameters['contractType']) && $parameters['contractType'] == CONTRACT_TYPE_DAILY_RENT) {
                $where[] = 'a_daily_hidden.group_id is NULL';
            }

            //with this price for squre meter can be calculated
            if ((isset($parameters['order'])) && (in_array('price-sqm', $parameters['order']))) {
                $where[] = "a_p.area_total > 0";
            }

        }
        if (empty($where))
            return '';

        return ' WHERE ' . implode(' AND ', $where);
    }

    protected static $ORDERS = array(
        'rank' => 'a_p.rank DESC',
        'district' => 'a_p.district ASC',
        'street' => 'a_p.street ASC',
        'price' => 'a_p.price_usd ASC',
        'price-sqm' => 'a_p.price_sqm_usd ASC',
        'add-time' => 'a_p.add_time DESC',
        'update-time' => 'a_p.update_time DESC',
        'update-date' => 'DATE(a_p.update_time) DESC',
        'update-month' => 'ROUND((UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(update_time)) / 2592000) ASC',
        'premium' => 'a_p.premium DESC',
        'premium2' => 'premium2 DESC',
        'has-images' => 'a_p.has_images = 1 DESC'
    );

    protected function constructOrder($parameters) {
        if (isset($parameters['order']) && !empty($parameters['order'])) {
            $orders = array();
            foreach ($parameters['order'] as $order)
                $orders[] = self::$ORDERS[$order];
            return ' ORDER BY ' . join(', ', $orders);
        }
        return '';
    }

}

?>