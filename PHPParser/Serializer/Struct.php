<?php

class PHPParser_Serializer_Struct implements PHPParser_Serializer
{

    public function serialize(array $nodes) {        

        return $this->_serialize($nodes);
        
    }

    protected function _serialize($node) {
        if ($node instanceof PHPParser_Node) {
			$result = array('_' => $node->getType());            
            foreach ($node->getAttributes() as $name => $value)
				$result[$name] = $value;
            foreach ($node as $name => $subNode)
                $result[$name] = $this->_serialize($subNode);
            return $result;
		}

        if ($node instanceof PHPParser_Comment) {
			return array('_' => 'Comment',
						 'isDocComment' => $node instanceof PHPParser_Comment_Doc,
						 'text' => $node->getText());
		}

        if (is_array($node)) {
            $result = array();
            foreach ($node as $subNode)
                $result[] = $this->_serialize($subNode);
            return $result;
		}

        if (is_string($node) || is_int($node) || is_float($node) 
		    || true === $node || false === $node || null === $node) {
            return $node;
		}

    	throw new InvalidArgumentException('Unexpected node type');
    }
}
