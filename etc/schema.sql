create table "ETL_EXT_KYC"."V_KY_TYPE" (
	M_ID INT NOT NULL,
	F_CODE VARCHAR2(50) NOT NULL,	
	CODE VARCHAR2(50) NOT NULL,
	NAME VARCHAR2(200),
	CLASS_ID CHAR(1) DEFAULT '2',
	LAST_VER TIMESTAMP,
	PRIMARY KEY(F_CODE, CODE)
);

comment on table V_KY_TYPE is '项目分类对照表';
comment on column V_KY_TYPE.M_ID is '数据同步流水号';
comment on column V_KY_TYPE.F_CODE is '父级分类代码';
comment on column V_KY_TYPE.CODE is '分类代码';
comment on column V_KY_TYPE.NAME is '分类名称';
comment on column V_KY_TYPE.CLASS_ID is '项目类型';
comment on column V_KY_TYPE.LAST_VER is '数据更新时间';

create table "ETL_EXT_KYC"."V_KY_DEPART"
(
	M_ID INT NOT NULL,
	CODE VARCHAR2(50) NOT NULL,
	NAME VARCHAR2(200),
	LAST_VER TIMESTAMP,
	PRIMARY KEY(CODE)
);

comment on table V_KY_DEPART is '部门信息对照表';
comment on column V_KY_DEPART.M_ID is '数据同步流水号';
comment on column V_KY_DEPART.CODE is '部门代码';
comment on column V_KY_DEPART.NAME is '部门名称';
comment on column V_KY_DEPART.LAST_VER is '数据更新时间';


CREATE TABLE "ETL_EXT_KYC"."V_KY_PROJ" (
	M_ID INT NOT NULL,
	WID VARCHAR2(50) NOT NULL,
	KY_PRJ_CODE VARCHAR2(50) NOT NULL,
	KY_PRJ_NAME VARCHAR2(500),
	CW_PRJ_CODE VARCHAR2(50),
	CW_PRJ_NAME VARCHAR2(500),
	KY_ORD VARCHAR2(50),
	KY_TYPE VARCHAR2(200),
	SNO VARCHAR2(50),
	SNAME VARCHAR2(200),
	TEL CHAR(20),
	START_YEAR CHAR(4),
	END_YEAR CHAR(4),
    CREATE_DATE CHAR(10),
	FINISH_DATE CHAR(10),
	CHECK_DATE CHAR(10),
	DNO VARCHAR2(50),
	DEPART VARCHAR2(200),
	MDO VARCHAR2(50) DEFAULT '000593',
	MDEPART VARCHAR2(200) DEFAULT '科研管理部',
	SA_SRC CHAR(100),
	PLAN_AMT NUMBER(14,2) DEFAULT 0,
	ATTACH NUMBER(14,2) DEFAULT 0,
	OUT_AMT NUMBER(14,2) DEFAULT 0,
	CLASS_ID CHAR(1) DEFAULT '2',
	PZ_CODE VARCHAR2(100),
	REMARK VARCHAR2(1000),
	KY_DOC VARCHAR2(4000),
	LAST_VER TIMESTAMP,
	PRIMARY KEY(WID)
);

comment on table V_KY_PROJ is '科研立项信息';
comment on column V_KY_PROJ.M_ID is '数据同步流水号';
comment on column V_KY_PROJ.WID is '项目编号';
comment on column V_KY_PROJ.KY_PRJ_CODE is '项目代码';
comment on column V_KY_PROJ.KY_PRJ_NAME is '项目名称';
comment on column V_KY_PROJ.CW_PRJ_CODE is '财务项目代码';
comment on column V_KY_PROJ.CW_PRJ_NAME is '财务项目名称';
comment on column V_KY_PROJ.KY_ORD is '项目类别代码';
comment on column V_KY_PROJ.KY_TYPE is '项目类别名称';
comment on column V_KY_PROJ.SNO is '负责人工号';
comment on column V_KY_PROJ.SNAME is '负责人姓名';
comment on column V_KY_PROJ.TEL is '负责人联系方式';
comment on column V_KY_PROJ.START_YEAR is '开始年度';
comment on column V_KY_PROJ.END_YEAR is '结题年度';
comment on column V_KY_PROJ.CREATE_DATE is '立项日期';
comment on column V_KY_PROJ.FINISH_DATE is '结题日期';
comment on column V_KY_PROJ.CHECK_DATE is '审核日期';
comment on column V_KY_PROJ.DNO is '所属部门代码';
comment on column V_KY_PROJ.DEPART is '所属部门名称';
comment on column V_KY_PROJ.MDO is '主管部门代码';
comment on column V_KY_PROJ.MDEPART is '主管部门名称';
comment on column V_KY_PROJ.SA_SRC is '项目来源';
comment on column V_KY_PROJ.PLAN_AMT is '立项经费';
comment on column V_KY_PROJ.ATTACH is '配套经费';
comment on column V_KY_PROJ.OUT_AMT is '外拨经费';
comment on column V_KY_PROJ.CLASS_ID is '项目类型';
comment on column V_KY_PROJ.PZ_CODE is '批准号';
comment on column V_KY_PROJ.REMARK is '备注';
comment on column V_KY_PROJ.KY_DOC is '附件';
comment on column V_KY_PROJ.LAST_VER is '数据更新时间';


CREATE TABLE "ETL_EXT_KYC"."V_KY_PROJ_BUDGET" (
	M_ID INT NOT NULL,
	WID VARCHAR2(50) NOT NULL,
	KY_PRJ_CODE VARCHAR2(50) NOT NULL,
	CW_PRJ_CODE VARCHAR2(50),
	BU_CODE VARCHAR2(50) NOT NULL,
	BU_NAME VARCHAR2(200),
	PLAN_AMT NUMBER(12,2) DEFAULT 0,
	LAST_VER TIMESTAMP,
	PRIMARY KEY(WID, BU_CODE)
);

comment on table V_KY_PROJ_BUDGET is '科研预算信息';
comment on column V_KY_PROJ_BUDGET.M_ID is '数据同步流水号';
comment on column V_KY_PROJ_BUDGET.WID is '项目编号';
comment on column V_KY_PROJ_BUDGET.KY_PRJ_CODE is '项目代码';
comment on column V_KY_PROJ_BUDGET.CW_PRJ_CODE is '财务项目代码';
comment on column V_KY_PROJ_BUDGET.BU_CODE is '预算科目代码';
comment on column V_KY_PROJ_BUDGET.BU_NAME is '预算科目名称';
comment on column V_KY_PROJ_BUDGET.PLAN_AMT is '预算金额';
comment on column V_KY_PROJ_BUDGET.LAST_VER is '数据更新时间';


CREATE TABLE "ETL_EXT_KYC"."V_KY_ARRI" (
	M_ID INT NOT NULL,
	ARRI_NO VARCHAR2(50) NOT NULL,
	ORD INT NOT NULL,
	FNO CHAR(30),
	SUBJ CHAR(40),
	BK_UNIT VARCHAR2(80),
	ABST VARCHAR2(80),
	OPT VARCHAR2(20),
    KY_PRJ_CODE VARCHAR2(50) NOT NULL,
	CW_PRJ_CODE VARCHAR2(50),
	ARRI_AMT NUMBER(14,2),
	F1 NUMBER(14,2) DEFAULT 0,
	F2 NUMBER(14,2) DEFAULT 0,
	F3 NUMBER(14,2) DEFAULT 0,
	F4 NUMBER(14,2) DEFAULT 0,
	F5 NUMBER(14,2) DEFAULT 0,
	MAIN_KEY CHAR(128),
	SMARK CHAR(25),
	ARRI_ENDDATE DATE,
	KY_DOC VARCHAR2(4000),
	LAST_VER TIMESTAMP,
	PRIMARY KEY(ARRI_NO, ORD)
);

comment on table V_KY_ARRI is '科研到款信息';
comment on column V_KY_ARRI.M_ID is '数据同步流水号';
comment on column V_KY_ARRI.ARRI_NO is '到款编号';
comment on column V_KY_ARRI.ORD is '到款细分号';
comment on column V_KY_ARRI.FNO is '财务往来号';
comment on column V_KY_ARRI.SUBJ is '科目代码';
comment on column V_KY_ARRI.BK_UNIT is '拨款单位';
comment on column V_KY_ARRI.ABST is '摘要';
comment on column V_KY_ARRI.OPT is '经办人';
comment on column V_KY_ARRI.KY_PRJ_CODE is '项目代码';
comment on column V_KY_ARRI.CW_PRJ_CODE is '财务项目代码';
comment on column V_KY_ARRI.ARRI_AMT is '入账金额';
comment on column V_KY_ARRI.F1 is '分成金额1';
comment on column V_KY_ARRI.F2 is '分成金额2';
comment on column V_KY_ARRI.F3 is '分成金额3';
comment on column V_KY_ARRI.F4 is '分成金额4';
comment on column V_KY_ARRI.F5 is '分成金额5';
comment on column V_KY_ARRI.MAIN_KEY is '到款往来标识';
comment on column V_KY_ARRI.SMARK is '到款往来辅助标识';
comment on column V_KY_ARRI.ARRI_ENDDATE is '经费关卡日期';
comment on column V_KY_ARRI.KY_DOC is '附件';
comment on column V_KY_ARRI.LAST_VER is '数据更新时间';

