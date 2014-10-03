<?php

class ClassParser extends Parser {
	private function detectsNamespace($tokens) {
		$namespace = '';
		while (list($index, $token) = each($this->tkns)) {
			list($id, $text) = $this->get_token($token);
			$this->ptr = $index;
			switch ($id) {
				case T_NAMESPACE:
					do {
						list($id, $text) = $this->walk_next_token();
						if (T_WHITESPACE === $id) {
							continue;
						}
						$namespace .= $text;
					} while ($id != ';');
					break 2;
			}
		}
		$namespace = substr($namespace, 0, -1) . '\\';
		return $namespace;
	}
	public function parse($source) {
		$parsed_classes = [];
		$parsed_extended_classes = [];
		$parsed_implemented_classes = [];
		$this->tkns = token_get_all($source);
		$this->code = '';

		$namespace = $this->detectsNamespace($this->tkns);
		reset($this->tkns);
		while (list($index, $token) = each($this->tkns)) {
			list($id, $text) = $this->get_token($token);
			$this->ptr = $index;
			switch ($id) {
				case T_CLASS:
					$class_name = null;
					$extends = null;
					$implements = null;
					// Seek for class name
					list($id, $text) = $this->walk_next_token();
					$class_name = $text;

					list($id, $text) = $this->walk_next_token();
					if (T_EXTENDS == $id) {
						list($id, $text) = $this->walk_next_token();
						$extends = $text;
					}

					if (T_IMPLEMENTS == $id) {
						list($id, $text) = $this->walk_next_token();
						$implements = $text;
					}

					$this->debug('[' . $class_name . ' e:' . $extends . ' i:' . $implements . ']');
					$parsed_classes[$namespace . $class_name][] = [
						'filename' => $this->filename,
						'extends' => $extends,
						'implements' => $implements
					];
					if (!empty($extends)) {
						$parsed_extended_classes[$extends] = [
							'filename' => $this->filename,
							'extended_by' => $class_name,
							'implements' => $implements
						];
					}
					if (!empty($implements)) {
						$parsed_implemented_classes[$implements] = [
							'filename' => $this->filename,
							'implemented_by' => $class_name,
							'extends' => $extends
						];
					}
					break;
			}
		}
		return [
			$parsed_classes,
			$parsed_extended_classes,
			$parsed_implemented_classes,
		];
	}
}
abstract class Parser {
	protected $filename = '';
	protected $debug = '';
	protected $indent_size = 1;
	protected $indent_char = "\t";
	protected $block_size = 1;
	protected $new_line = "\n";
	protected $indent = 0;
	protected $for_idx = 0;
	protected $code = '';
	protected $ptr = 0;
	protected $tkns = 0;
	public function __construct($filename, $debug) {
		$this->filename = $filename;
		$this->debug = $debug;
	}
	abstract public function parse($source);
	protected function get_token($token) {
		if (is_string($token)) {
			return array($token, $token);
		} else {
			return $token;
		}
	}
	protected function append_code($code = "", $trim = true) {
		if ($trim) {
			$this->code = rtrim($this->code) . $code;
		} else {
			$this->code .= $code;
		}
	}
	protected function get_crlf_indent($in_for = false, $increment = 0) {
		if ($in_for) {
			$this->for_idx++;
			if ($this->for_idx > 2) {
				$this->for_idx = 0;
			}
		}
		if ($this->for_idx === 0 || !$in_for) {
			return $this->get_crlf() . $this->get_indent($increment);
		} else {
			return $this->get_space(false);
		}
	}
	protected function get_crlf($true = true) {
		return $true ? $this->new_line : "";
	}
	protected function get_space($true = true) {
		return $true ? " " : "";
	}
	protected function get_indent($increment = 0) {
		return str_repeat($this->indent_char, ($this->indent + $increment) * $this->indent_size);
	}
	protected function set_indent($increment) {
		$this->indent += $increment;
		if ($this->indent < 0) {
			$this->indent = 0;
		}
	}
	protected function inspect_token($delta = 1) {
		if (!isset($this->tkns[$this->ptr + $delta])) {
			return [null, null];
		}
		return $this->get_token($this->tkns[$this->ptr + $delta]);
	}
	protected function is_token($token, $prev = false, $i = 99999, $idx = false) {
		if ($i === 99999) {
			$i = $this->ptr;
		}
		if ($prev) {
			while (--$i >= 0 && is_array($this->tkns[$i]) && $this->tkns[$i][0] === T_WHITESPACE);
		} else {
			while (++$i < sizeof($this->tkns) - 1 && is_array($this->tkns[$i]) && $this->tkns[$i][0] === T_WHITESPACE);
		}
		if (isset($this->tkns[$i]) && is_string($this->tkns[$i]) && $this->tkns[$i] === $token) {
			return $idx ? $i : true;
		} elseif (is_array($token) && isset($this->tkns[$i]) && is_array($this->tkns[$i])) {
			if (in_array($this->tkns[$i][0], $token)) {
				return $idx ? $i : true;
			} elseif ($prev && $this->tkns[$i][0] === T_OPEN_TAG) {
				return $idx ? $i : true;
			}
		}
		return false;
	}
	protected function prev_token() {
		$i = $this->ptr;
		while (--$i >= 0 && is_array($this->tkns[$i]) && $this->tkns[$i][0] === T_WHITESPACE);
		return $this->tkns[$i];
	}
	protected function walk_next_token() {
		$i = $this->ptr;
		$sizeof_tokens = sizeof($this->tkns);
		while (++$i <= $sizeof_tokens && is_array($this->tkns[$i]) && $this->tkns[$i][0] === T_WHITESPACE);
		$this->ptr = $i;
		if (!isset($this->tkns[$i])) {
			return null;
		}
		return $this->get_token($this->tkns[$i]);
	}
	protected function has_ln_after() {
		$id = null;
		$text = null;
		list($id, $text) = $this->inspect_token();
		return T_WHITESPACE === $id && substr_count($text, PHP_EOL) > 0;
	}
	protected function has_ln_before() {
		$id = null;
		$text = null;
		list($id, $text) = $this->inspect_token(-1);
		return T_WHITESPACE === $id && substr_count($text, PHP_EOL) > 0;
	}
	protected function has_ln_prev_token() {
		list($id, $text) = $this->get_token($this->prev_token());
		return substr_count($text, PHP_EOL) > 0;
	}
	protected function substr_count_trailing($haystack, $needle) {
		$cnt = 0;
		$i = strlen($haystack) - 1;
		for ($i = $i; $i >= 0; $i--) {
			$char = substr($haystack, $i, 1);
			if ($needle === $char) {
				$cnt++;
			} elseif (' ' !== $char && "\t" !== $char) {
				break;
			}
		}
		return $cnt;
	}
	protected function debug($msg) {
		$this->debug && fwrite(STDERR, $msg . PHP_EOL);
	}
}

if (!isset($argv[1])) {
	exit(255);
}
$cmd = trim(strtolower($argv[1]));
$ignoreList = [];
$ignoreListFn = 'oracle.ignore';
if (file_exists($ignoreListFn)) {
	$ignoreList = file($ignoreListFn);
}
$fnDb = 'oracle.serialize';
if (!file_exists($fnDb) || 'flush' == $cmd) {
	fwrite(STDERR, "Database not found... generating" . PHP_EOL);
	$debug = false;
	$uri = $argv[2];

	$dir = new RecursiveDirectoryIterator($uri);
	$it = new RecursiveIteratorIterator($dir);
	$files = new RegexIterator($it, '/^.+\.php$/i', RecursiveRegexIterator::GET_MATCH);
	$all_classes = [];
	$all_extends = [];
	$all_implements = [];
	foreach ($files as $file) {
		$file = $file[0];
		foreach ((array) $ignoreList as $ignore) {
			$ignore = trim($ignore);
			if (
				substr(str_replace(getcwd() . '/', '', $file), 0, strlen($ignore)) == $ignore ||
				substr($file, 0, strlen($ignore)) == $ignore
			) {
				continue 2;
			}
		}
		echo $file, PHP_EOL;

		$content = file_get_contents($file);

		list($class, $extends, $implements) = (new ClassParser($file, $debug))->parse($content);
		$all_classes = array_merge_recursive($all_classes, $class);
		$all_extends = array_merge_recursive($all_extends, $extends);
		$all_implements = array_merge_recursive($all_implements, $implements);
	}
	fwrite(STDERR, "Serializing and storing..." . PHP_EOL);
	file_put_contents(
		$fnDb, serialize([
			'all_classes' => $all_classes,
			'all_extends' => $all_extends,
			'all_implements' => $all_implements,
		])
	);
} else {
	if (time() - filemtime($fnDb) > 86400) {
		fwrite(STDERR, "Warning: database file older than a day" . PHP_EOL);
	}
	$db = unserialize(file_get_contents($fnDb));

	$all_classes = $db['all_classes'];
	$all_extends = $db['all_extends'];
	$all_implements = $db['all_implements'];
}

if ("implements" == $cmd) {
	if (!isset($all_implements[$argv[2]])) {
		fwrite(STDERR, "Interface not found: " . $argv[2] . PHP_EOL);
		exit(255);
	}
	$found_implements = &$all_implements[$argv[2]];
	echo $argv[2] . ' implemented by' . PHP_EOL;
	if (is_array($found_implements['implemented_by'])) {
		foreach ($found_implements['implemented_by'] as $idx => $class_name) {
			echo "\t", $class_name, " - ", $found_implements["filename"][$idx], PHP_EOL;
		}
	} else {
		echo "\t", $found_implements['implemented_by'], ' - ', $found_implements["filename"], PHP_EOL;
	}
	echo PHP_EOL;
}

if ("extends" == $cmd) {
	if (!isset($all_extends[$argv[2]])) {
		fwrite(STDERR, "Class not found: " . $argv[2] . PHP_EOL);
		exit(255);
	}
	$found_extends = &$all_extends[$argv[2]];
	echo $argv[2] . ' extended by' . PHP_EOL;
	foreach ($found_extends['extended_by'] as $idx => $class_name) {
		echo "\t", $class_name, " - ", $found_extends["filename"][$idx], PHP_EOL;
	}
	echo PHP_EOL;
}

if ("class" == $cmd) {
	if (!isset($argv[2]) || !isset($all_classes[$argv[2]])) {
		isset($argv[2]) && fwrite(STDERR, "Class not found: " . $argv[2] . PHP_EOL);
		fwrite(STDERR, 'Classes available:' . PHP_EOL . implode(PHP_EOL, array_keys($all_classes)) . PHP_EOL);
		exit(255);
	}
	$found_classes = &$all_classes[$argv[2]][0];
	echo $argv[2], PHP_EOL;
	if (!empty($found_classes['extends'])) {
		echo "\t extends ", $found_classes['extends'], PHP_EOL;
	}

	if (!empty($found_classes['implements'])) {
		echo "\t implements ", $found_classes['implements'], PHP_EOL;
	}

	echo PHP_EOL;
}