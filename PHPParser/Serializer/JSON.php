<?php

class PHPParser_Serializer_JSON implements PHPParser_Serializer
{

	protected $structSerializer;

    /**
     * Constructs a JSON serializer.
     */
    public function __construct() {
        $this->structSerializer = new PHPParser_Serializer_Struct;
    }


    public function serialize(array $nodes) {        

        return json_encode($this->structSerializer->serialize($nodes));
        
    }

}
