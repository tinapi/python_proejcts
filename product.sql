create table product (
	id int auto_increment primary key,
	title varchar(500) character set utf8 collate utf8_general_ci,
	brand varchar(200) character set utf8 collate utf8_general_ci,
	rate float,
	price decimal(10,2)
	reviewCount int(5)
)