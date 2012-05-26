<?php
/**
 * @property int $id
 * @property City $city
 * @property District $district
 * @property string $realName
 * @property array $addresses
 * @property array $nearBuilding
 * @property string $url
 * @property string $innerUrl
 * @property string $urlByRank
 * @property string discussion
 * @property array $photo
 * @property array $photos
 * @property string $company
 */
class Building extends _Building {

    public function getId() {
        return $this->_n_id;
    }

    protected function getCity() {
        return City::factory()->findById($this->_city);
    }

    protected function getDistrict() {
        return District::factory()->findById($this->_district);
    }

    protected function getRealName() {
        return $this->_name;
    }

    protected function getNearBuilding() {
        $sql = "SELECT b1.*,
                      (b1.latitude - b2.latitude) * (b1.latitude - b2.latitude) + (b1.longitude - b2.longitude) * (b1.longitude - b2.longitude) as dst
                FROM n_building as b1
                  INNER JOIN n_building as b2
                   ON b2.n_id = {$this->nId}
                  AND b1.city = b2.city
                  AND b1.n_id <> b2.n_id
                WHERE b1.name <> ''
        ORDER BY dst LIMIT 4";
        return $this->factory()->findAllBySql($sql);
    }

    protected function getAddresses() {
        $sql = "
          SELECT
            n_street.street_id,
            CONCAT(interface_geo_streets.nominative, ' ', interface_geo_street_types.short) AS short_name,
            house
          FROM n_street
          INNER JOIN interface_geo_streets
                  ON interface_geo_streets.street_id = n_street.street_id
          INNER JOIN interface_geo_street_types USING(street_type_id)
          WHERE n_street.n_id = {$this->nId}
          ORDER BY n_street.street_id
        ";
        return $this->sql($sql)->queryAll();
    }

    protected function getName() {
        if (empty($this->_name))
            return $this->address;
        if (strpos($this->_name, '"') !== false)
            return $this->_name;
        return 'ЖК ' . $this->_name;
    }

    protected function getJustName() {
        if (empty($this->_name))
            return $this->address;
        return $this->_name;
    }

    protected function getUrl() {
        if (isset($this->site) && (!empty($this->site)))
            return Yii::app()->createUrl('redirect', array('to' => 'http://' . $this->site));
        return 'http://novostroyki.lun.ua/' . Decorator::format($this->name) . '-' . $this->nId;
    }

    protected function getInnerUrl()
    {
        return 'http://novostroyki.lun.ua/' . Decorator::format($this->name) . '-' . $this->nId;
    }

    protected function getUrlByRank()
    {
        return ( $this->rank <= 10 ) ? $this->innerUrl : $this->url;
    }

    protected function getDiscussion() {
        $query = "SELECT * FROM n_discussion WHERE n_id=" . $this->nId;
        $res = $this->sql($query)->queryAll();
        if (empty($res)) return false;
        $disc = $res[0]['url'];
        foreach ($res as $row) {
            if (strpos($row['url'], 'www.domik')) {
                $disc = $row['url'];
            }
        }
        return Yii::app()->createUrl('redirect', array('to' => 'http://' . $disc));
    }

    public function getLink($substitute = null) {
        if (empty($this->realName)) {
            return '<a target="_blank" href="' . $this->urlByRank . '">' . (($substitute == null) ? $this->name : $substitute) . '</a>';
        } else {
            return '<a target="_blank" href="' . $this->urlByRank . '">' . $this->realName . '</a>';
        }
    }

    protected function getPhoto() {
        return $this->sql('SELECT `name` FROM n_image WHERE n_id = ' . $this->nId . ' ORDER BY position LIMIT 1')->queryScalar();
    }

    protected function getPhotos() {
        return $this->sql('SELECT `name` FROM n_image WHERE n_id = ' . $this->nId . ' ORDER BY position LIMIT 5')->queryColumn();
    }

    /**
     * Getter for builder company
     *
     * @return void
     */
    public function getCompany()
    {
        //return "n_id = ".$this->nId;
        return $this->sql('SELECT n_company.name
                    FROM n_to_company
                    JOIN n_company ON n_company.id = n_to_company.c_id AND n_to_company.type="Реализует проект" AND n_to_company.n_id = ' . $this->nId . '
                    LIMIT 1')->queryScalar();
    }

    protected function getCityId() {
        return $this->_city;
    }

    protected function getDistrictId() {
        return $this->_district;
    }

    protected  function getTextState() {
        switch ($this->state)
        {
            case 0:
                return "Строится";
            case 1:
                return "Готово";
            case 2:
                return "В проекте";
        }
    }

    protected  function getTextClass() {
        switch ($this->class)
        {
            case 0:
                return '-';
            case 1:
                return 'эконом';
            case 2:
                return 'бизнес';
            case 3:
                return 'элит';
        }
    }

    public function getIsPopular() {
        return $this->rank > 1;
    }

}

class BuildingFactory extends _BuildingFactory {

    protected function getCacheTime() {
        return 60 * 60;
    }

    public function findByName($buildingName, $city) {
        $buildingName = str_replace('  ', ' ', trim(str_replace('ЖК', '', $buildingName)));
        $sql = "SELECT n_building.* FROM n_building
         WHERE
             n_building.city = $city
             AND (n_building.name LIKE '%$buildingName%'
                  OR
                  EXISTS(SELECT * FROM residential_complexes_synonims
                         WHERE residential_complexes_synonims.owner_id = n_building.n_id
                           AND residential_complexes_synonims.name LIKE '%$buildingName%'))";
        return $this->findBySql($sql);
    }


    /**
     * Top buildings in this city
     *
     * @param $search
     * @param $limit
     * @return array
     */
    public function getTopBuildings( $search, $limit = 40 )
    {
        $query = "SELECT * FROM (
              SELECT n_b.*
                  FROM n_seo AS n_s
              JOIN n_building AS n_b
                  ON n_b.n_id = n_s.n_id
                 AND n_b.city = {$search->city->id}
              ORDER BY n_s.frequency DESC LIMIT $limit
        ) as dt ORDER BY dt.name = '' ASC, dt.name ASC";
        $res = $this->findAllBySql($query);
        return $res;
    }

    /**
     * Returns buildings from adjacent cities (from same region) that have most advertisements. Ordered by name
     *
     * @param $search
     * @param $limit
     * @return array
     */
    public function getPopularComplexesInAdjacentCities($search, $limit = 20) {
        $query = "SELECT * FROM (
           SELECT n_b . *
           FROM n_seo AS n_s
           JOIN n_building AS n_b
               ON n_b.n_id = n_s.n_id
              AND n_b.city <> {$search->city->id}
              AND n_b.region = {$search->city->region->id}
           ORDER BY n_s.frequency DESC
           LIMIT $limit
        ) AS td
        ORDER BY td.name =  '' ASC , td.name ASC";
        return $this->findAllBySql($query);
    }

    protected function getSerializeParameters() {
        return array(
            'id',
            'name',
            'address',
            'cityId',
            'districtId',
            'mainImg',
            'photos',
            'class',
            'textClass',
            'state',
            'textState',
            'latitude',
            'longitude',
            'minPriceSqm',
            'maxPriceSqm',
            'isPopular',
        );
    }

}
