USE narou_db;
CREATE TABLE IF NOT EXISTS contents_tbl
(
    id  INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(id),
    count INT NOT NULL,
    ncode   VARCHAR(10) NOT NULL,
    title   VARCHAR(100),
    userid  INT,
    writer  VARCHAR(100),
    story   VARCHAR(1000),
    biggenre    INT,
    genre   INT,
    gensaku VARCHAR(10),
    keyword VARCHAR(100),
    general_firstup DATETIME,
    general_lastup  DATETIME,
    novel_type  INT,
    end INT,
    general_all_no  INT,
    length  INT,
    time    INT,
    isstop  INT,
    isr15   INT
);

CREATE TABLE IF NOT EXISTS parameter_tbl
(
    parameter_name  VARCHAR(30) NOT NULL,
    parameter_value   INT
);

INSERT INTO parameter_tbl SET parameter_name = 'counter', parameter_value = 0;

CREATE TABLE IF NOT EXISTS count_timestamp_tbl
(
    count   INT NOT NULL,
    timestamp   DATETIME NOT NULL
);

