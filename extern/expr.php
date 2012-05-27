<?php
/**
 * Не бойся, это всего лишь php внутри php.
 */

require_once('utils.php');

class SearchCodeGenerator extends CodeGenerator {

    /** @var SearchBase */
    protected $search;
    /** @var ReflectionClass */
    protected $reflector;
    protected $meta;
    protected $specificMethods = array();

    protected function one($value) {
        return "(is_array($value) ? (empty($value) ? null : array_shift($value)) : $value)";
    }

    protected function many($value) {
        return "(is_array($value) ? $value : (empty($value) ? array() : array($value)))";
    }

    protected function is_instance($obj, $class) {
        return "(!is_string($obj) && is_a($obj, '$class'))";
    }

    protected function constructGetter($name, $property) {
        $methodName = 'get' . ucwords($name);
        if (isset($this->specificMethods[$methodName])) {
            $this->insertMethodCode($this->specificMethods[$methodName]);
            unset($this->specificMethods[$methodName]);
            return;
        }
        if (isset($property['getter'])) {
            $this->open("protected function $methodName()");
            $this->line("return {$property['getter']};");
            $this->close();
            $this->line();
        }
    }

    protected function hasGetter($name) {
        return isset($this->specificMethods['get' . ucwords($name)]) || isset($this->meta[$name]['getter']);
    }

    protected function constructSetter($name, $property) {
        $methodName = 'set' . ucwords($name);
        if (isset($this->specificMethods[$methodName])) {
            $this->insertMethodCode($this->specificMethods[$methodName]);
            unset($this->specificMethods[$methodName]);
            return;
        }
        if (in_array('virtual', $property))
            return;
        $this->open("public function $methodName(\$value)");
        if (isset($property['setter']))
            $setter = $property['setter'];
        elseif (isset($property['model'])) {
            $model = $property['model'];
            $setter = "{$this->is_instance('$value', $model)} ? \$value : {$model}::factory()->findById(\$value)";
        }
        if (isset($property['many'])) {
            $this->line("\$this->$name = array();");
            $this->line("\$values = {$this->many('$value')};");
            $this->open("foreach(\$values as \$value)");
            if (isset($setter))
                $this->line("\$value = $setter;");
            if ($property['many'] == 'unique') {
                $this->open("if (isset(\$value) && !in_array(\$value, \$this->$name))");
                $this->line("\$this->{$name}[] = \$value;");
                $this->close();
            } else {
                $this->open("if (isset(\$value))");
                $this->line("\$this->{$name}[] = \$value;");
                $this->close();
            }
            $this->close();
        } else {
            if (!isset($setter))
                $setter = '$value';
            $this->line("\$this->$name = $setter;");
        }
        $this->constructRelation($name);
        $this->close();
        $this->line();

    }

    protected $defaults = array();
    protected $relations = array();
    protected $exclusions = array();
    protected $relationStack = array();

    protected function constructRelation($name) {
        if (!isset($this->exclusions[$name]) && !isset($this->relations[$name]))
            return;
        $this->comment('unset relation properties');
        $this->deepRelation($name);
        if (isset($this->exclusions[$name])) {
            foreach ($this->exclusions[$name] as $relation) {
                $this->line("\$this->$relation = {$this->defaults[$relation]};");
                $this->deepRelation($relation);
            }
        }
    }

    protected function deepRelation($name) {
        if (!in_array($name, $this->relationStack)) {
            $this->relationStack[] = $name;
            if (isset($this->relations[$name]))
                foreach ($this->relations[$name] as $relation)
                    if (!in_array($relation, $this->relationStack)) {
                        $this->line("\$this->$relation = {$this->defaults[$relation]};");
                        $this->deepRelation($relation);
                    }
        }
    }

    protected function compileRelations() {
        foreach ($this->search->relations() as $key => $value)
            if (is_int($key)) { // отношения взаимоисключения
                foreach ($value as $lefts)
                    foreach ($value as $rights)
                        if ($lefts !== $rights)
                            $this->addRelations('exclusions', $lefts, $rights);
            } else // отношения зависимости
                $this->addRelations('relations', $key, $value);
    }

    protected function addRelations($type, $lefts, $rights) {
        $array = $this->$type;
        foreach (many($lefts) as $to) {
            if (!isset($array[$to]))
                $array[$to] = array();
            foreach (many($rights) as $from)
                if (!in_array($from, $array[$to]))
                    array_push($array[$to], $from);
        }
        $this->$type = $array;
    }

    protected function constructDocs() {
        $this->line('/**');
        foreach ($this->meta as $name => $property) {
            if (isset($property['type']))
                $type = $property['type'];
            elseif (isset($property['many']))
                $type = 'array';
            elseif (isset($property['model']))
                $type = $property['model'];
            else
                $type = 'string';
            $this->line(" * @property $type \$$name");
        }
        $this->line(' * @property array $properties');
        $this->line(' * @property array $propertiesAsId');
        $this->line(' */');
    }

    protected $rules = array();

    protected function compileRules() {
        foreach ($this->search->rules() as $message => $rule) {
            $scenarios = isset($rule['scenario']) ? explode(',', $rule['scenario']) : array(null);
            foreach ($scenarios as $scenario)
                if (!isset($this->rules[$scenario]))
                    $this->rules[$scenario] = array();
            unset($rule['scenario']);
            foreach ($rule as $precondition => $condition) {
                if (!is_int($precondition))
                    $condition = "($precondition) && !($condition)";
                else
                    $condition = "!($condition)";
                foreach ($scenarios as $scenario)
                    $this->rules[$scenario][] = array($message, $condition);
            }
        }
    }

    protected function addRule($rule) {
        $message = $rule[0]; $condition = $rule[1];
        $this->open("if ($condition)");
            $this->line("return '$message';");
        $this->close();
    }

    protected function constructRules() {
        $this->open('public function getError($scenario = null)');
        if (isset($this->rules[null])) {
            foreach ($this->rules[null] as $rule)
                $this->addRule($rule);
        }
        foreach ($this->rules as $scenario => $rules)
            if (!empty($scenario)) {
                $this->open("if (\$scenario == '$scenario')");
                    foreach ($rules as $rule)
                        $this->addRule($rule);
                    $this->line('return null;');
                $this->close();
            }
            $this->line('return null;');
        $this->close();
    }

    protected function constructUnsetPrivate() {
        $this->open('protected function unsetPrivateProperty()');
        foreach ($this->meta as $name => $property)
            if (in_array('private', $property))
                $this->line("\$this->$name = {$this->defaults[$name]};");
        $this->close();
    }

    protected function constructGetProperties() {
        $this->open("protected function getProperties()");
        $this->line('$properties = get_object_vars($this);');
        foreach ($this->meta as $name => $property)
            if (!in_array('virtual', $property)) {
                $methodName = 'get' . ucwords($name);
                if (isset($this->specificMethods[$methodName])) {
                    $this->line("\$properties['$name'] = \$this->$methodName();");
                }
            }
        $this->line('return array_filter($properties);');
        $this->close();
    }

    protected function constructGetPropertiesAsId() {
        $this->open("protected function getPropertiesAsId()");
        $this->line('$properties = $this->properties;');
        foreach ($this->meta as $name => $property)
            if (!in_array('virtual', $property) && (isset($property['model']) || isset($property['key']))) {
                $key = isset($property['key']) ? $property['key'] : $name;
                $this->open("if (isset(\$properties['$name']))");
                if (isset($property['model'])) {
                    if (isset($property['many'])) {
                        $ids = $name != $key ? "\$properties['$key']" : '$ids';
                        $this->line("$ids = array();");
                        $this->open("foreach (\$properties['$name'] as \$model)");
                        $this->line("{$ids}[] = \$model->idValue;");
                        $this->close();
                        if ($name == $key)
                            $this->line("\$properties['$key'] = \$ids;");
                    } else {
                        $this->line("\$properties['$key'] = \$properties['$name']->idValue;");
                    }
                } else {
                    $this->line("\$properties['$key'] = \$properties['$name'];");
                }
                if ($name != $key)
                    $this->line("unset(\$properties['$name']);");
                $this->close();
            }
        $this->line('return $properties;');
        $this->close();
    }

    protected function constructPriorities() {
        $this->line('protected static $priorities = array('); $this->tab();
        $i = 0;
        foreach ($this->meta as $name => $property) {
            $i++;
            $this->line("'$name' => $i,");
        }
        $this->untab(); $this->line(');');
    }

    protected function generate() {
        $this->search = new SearchBase();
        $this->reflector = new ReflectionClass(get_class($this->search));
        $this->meta = $this->search->properties();
        $this->compileRelations();
        foreach ($this->reflector->getMethods(ReflectionMethod::IS_FINAL) as $method)
            $this->specificMethods[$method->getName()] = $method;
        $this->command('<?php');
        $this->comment("\n\tАХТУНГ! АЛАРМ! ปลุก!\n\tЭтот файл сгенерирован автоматически, потому тебе не стоит вручную его изменять.\n\tНо если все же очень хочется, попробуй настроить правильно SearchBase и выполнить комманду `php console.php research`.\n\tСкорее всего это именно то, что тебе на самом деле нужно. Good luck!\n");
        $this->line("require_once('utils.php');");
        $this->constructDocs();
        $this->open('class Search extends LComponent');
            $this->line();
            foreach ($this->meta as $name => $property)
                if (!in_array('virtual', $property)) {
                    if (isset($property['default'])) {
                        $this->defaults[$name] = $property['default'];
                    } else {
                        $this->defaults[$name] = isset($property['many']) ? 'array()' : 'null';
                    }
                    $modifier = $this->hasGetter($name) ? 'private' : 'public';
                    $this->line("$modifier \$$name = {$this->defaults[$name]};");
                }
            $this->line();
            $this->constructGetProperties();
            $this->line();
            $this->constructGetPropertiesAsId();
            $this->line();
            $this->constructPriorities();
            $this->line();
            foreach ($this->meta as $name => $property) {
                $this->comment("$name property");
                $this->line();
                $this->constructGetter($name, $property);
                $this->constructSetter($name, $property);
            }
            $this->constructUnsetPrivate(); $this->line();
            $this->comment("specific methods"); $this->line();
            foreach ($this->specificMethods as $method)
                $this->insertMethodCode($method);
            $this->compileRules();
            $this->constructRules(); $this->line();
        $this->close();
    }

    protected function insertMethodCode($method) {
        $start = $method->getStartLine();
        $end = $method->getEndLine();
        $inputFile = fopen(__DIR__ . '/SearchBase.php', 'r');
        for ($i = 0; $i < $start - 1; $i++)
            fgets($inputFile);
        $this->command(PHP_EOL);
        for ($i = $start; $i <= $end; $i++)
            $this->command(fgets($inputFile));
        fclose($inputFile);
    }

    protected function getOutputFileName() {
        return 'search/Search';
    }
}
?>