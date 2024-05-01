CREATE TABLE `Students` (
  `Student ID` int NOT NULL PRIMARY KEY,
  `Student Name` VARCHAR(255) NOT NULL,
  `Date Of Birth` date NOT NULL,
  `Student Class` set('Math Class', 'IT Class', 'Literature Class') NOT NULL
);

INSERT INTO `Students` (`Student ID`, `Student Name`, `Date Of Birth`, `Student Class`) VALUES
	('1', 'John', '1984-10-11', 'IT Class'),
	('2', 'Mary', '1984-01-25', 'IT Class'),
	('3', 'Mike', '1984-07-12', 'Math Class'),
	('4', 'Nicholas', '1984-05-08', 'Math Class'),
	('5', 'Tom', '1984-12-08', 'Math Class'),
	('6', 'Peter', '1983-01-03', 'Literature Class'),
	('7', 'Martina', '1984-07-05', 'Literature Class'),
	('8', 'Teo', '1984-01-25', 'Literature Class');