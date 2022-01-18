USE narou_db;
CREATE TABLE IF NOT EXISTS contents_tbl
(
    id  INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(id),
    count INT NOT NULL,
    ncode   VARCHAR(10) NOT NULL,
    title   VARCHAR(200),
    userid  INT,
    writer  VARCHAR(1000),
    story   VARCHAR(1000),
    biggenre    INT,
    genre   INT,
    gensaku VARCHAR(10),
    keyword VARCHAR(1000),
    general_firstup DATETIME,
    general_lastup  DATETIME,
    novel_type  INT,
    end INT,
    general_all_no  INT,
    length  INT,
    time    INT,
    isstop  INT,
    isr15   INT,
    isbl    INT,
    isgl    INT,
    iszankoku   INT,
    istensei    INT,
    istenni INT,
    pc_or_k INT,
    global_point    INT,
    daily_point INT,
    weekly_point    INT,
    monthly_point   INT,
    quarter_point   INT,
    yearly_point    INT,
    fav_novel_cnt   INT,
    impression_cnt  INT,
    review_cnt  INT,
    all_point   INT,
    all_hyoka_cnt   INT,
    sasie_cnt   INT,
    kaiwaritu   INT,
    novelupdated_at DATETIME,
    updated_at  DATETIME
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

CREATE TABLE IF NOT EXISTS count_allcount_tbl
(
    count   INT NOT NULL,
    allcount    INT
);