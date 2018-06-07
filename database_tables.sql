-- TABLES and VIEWS built on PostgreSQL
-- TABLES
CREATE TABLE assets_onhand
(
  id serial NOT NULL,
  user_id integer,
  product_id integer,
  item_id character varying(100),
  location_flag character varying(100),
  location_type character varying(100),
  location_id character varying(100),
  qty integer,
  is_singleton boolean,
  CONSTRAINT b_assets_oh_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE build_pipeline
(
  id serial NOT NULL,
  user_id integer,
  product_id integer,
  blueprint_id integer,
  runs integer,
  material_id integer,
  material_qty integer,
  material_cost double precision,
  product_name character varying(100),
  material character varying(100),
  group_id integer,
  build_or_buy integer,
  jita_sell_price double precision,
  local_sell_price double precision,
  build_cost double precision,
  material_comp_id integer,
  status integer,
  CONSTRAINT b_pipeline_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE eve_sso
(
  id integer NOT NULL,
  client_id character varying(100),
  secret_key character varying(100),
  scope character varying(100),
  CONSTRAINT evesso_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);


CREATE TABLE invent_pipeline
(
  id serial NOT NULL,
  user_id integer,
  product_id integer,
  blueprint_id integer,
  runs integer,
  product_name character varying(100),
  datacore_id integer,
  datacore_qty integer,
  datacore_cost double precision,
  datacore character varying(100),
  status integer,
  CONSTRAINT i_pipeline_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE mining_calc
(
  id serial NOT NULL,
  user_id integer,
  m3_per_cycle integer,
  cycle_time integer,
  num_cycles integer,
  refinery double precision,
  trit_required integer,
  pye_required integer,
  mex_required integer,
  iso_required integer,
  nox_required integer,
  zyd_required integer,
  meg_required integer,
  morph_required integer,
  asteroid1_id integer,
  asteroid2_id integer,
  asteroid3_id integer,
  asteroid4_id integer,
  CONSTRAINT b_mining_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE role
(
  id serial NOT NULL,
  name character varying(80),
  description character varying(255),
  CONSTRAINT role_pkey PRIMARY KEY (id),
  CONSTRAINT role_name_key UNIQUE (name)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE roles_users
(
  user_id integer,
  role_id integer,
  CONSTRAINT roles_users_role_id_fkey FOREIGN KEY (role_id)
      REFERENCES role (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

CREATE TABLE ship_fittings
(
  id serial NOT NULL,
  build_id integer,
  user_id integer,
  ship_id integer,
  ship_name character varying(100),
  qty integer,
  num_rigslots integer,
  num_lowslots integer,
  num_medslots integer,
  num_highslots integer,
  component_id integer,
  component_qty integer,
  component_cost double precision,
  component character varying(100),
  component_slot character varying(20),
  contract_sell_price double precision,
  build_cost double precision,
  jita_buy double precision,
  rollup integer,
  CONSTRAINT b_shipfittings_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE users
(
  id serial NOT NULL,
  character_id character varying(100),
  character_name character varying(100),
  refresh_token character varying(255),
  expiration timestamp without time zone,
  auth_code character varying(255),
  active boolean,
  last_logged_in timestamp without time zone,
  CONSTRAINT user_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE wallet_journal
(
  id serial NOT NULL,
  user_id character varying(100),
  amount double precision,
  date_transaction timestamp without time zone,
  transaction_id character varying(100),
  ref_type character varying(100),
  CONSTRAINT wallet_journal_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE wallet_transactions
(
  id serial NOT NULL,
  user_id character varying(100),
  amount double precision,
  date_transaction timestamp without time zone,
  transaction_id character varying(100),
  client_id character varying(100),
  location_id character varying(100),
  qty integer,
  product_id integer,
  CONSTRAINT wallet_transaction_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);



-- VIEWS
CREATE OR REPLACE VIEW v_asteroid_groups AS
 SELECT DISTINCT invgroups."groupID" AS id,
    invgroups."groupName" AS "group"
   FROM invgroups
  WHERE invgroups."categoryID" = 25 AND invgroups."groupID" <> 903
  ORDER BY invgroups."groupID";

  CREATE OR REPLACE VIEW v_asteroids AS
 SELECT invtypes."typeID" AS id,
    invgroups."groupID" AS group_id,
    invtypes."typeName" AS asteroid,
    invtypes.volume AS vol,
    invtypes."portionSize" AS portion
   FROM invtypes,
    invgroups
  WHERE invgroups."groupID" = invtypes."groupID" AND invgroups."categoryID" = 25 AND invgroups."groupID" <> 903 AND invtypes."portionSize" > 1
  ORDER BY invgroups."groupID", invtypes."typeID";

  CREATE OR REPLACE VIEW v_build_components AS
 SELECT t."typeID" AS id,
    t2."typeName" AS material,
    t2."typeID" AS material_id,
    m.quantity
   FROM invtypes t,
    "invTypeMaterials" m,
    invtypes t2
  WHERE m."typeID" = t."typeID" AND t2."typeID" = m."materialTypeID";

  CREATE OR REPLACE VIEW v_build_pipeline_products AS
 SELECT DISTINCT build_pipeline.product_name,
    build_pipeline.user_id,
    build_pipeline.blueprint_id,
    build_pipeline.product_id,
    build_pipeline.runs,
    build_pipeline.jita_sell_price,
    build_pipeline.local_sell_price,
    build_pipeline.build_cost,
    build_pipeline.status
   FROM build_pipeline;

   CREATE OR REPLACE VIEW v_build_product AS
 SELECT t."typeID" AS id,
    t2."typeName" AS t2_blueprint,
    p."productTypeID" AS t2_id
   FROM invtypes t,
    "industryActivityProducts" p,
    invtypes t2
  WHERE t."typeID" = p."typeID" AND p."productTypeID" = t2."typeID" AND p."activityID" = 1
  ORDER BY t2."typeName";

  CREATE OR REPLACE VIEW v_build_requirements AS
 SELECT t."typeID" AS id,
    t2."typeName" AS material,
    t2."typeID" AS material_id,
    t2."groupID" AS group_id,
    m.quantity AS qty,
    ap."productTypeID" AS product_id
   FROM "industryActivityMaterials" m,
    invtypes t,
    invtypes t2,
    "industryActivityProducts" ap
  WHERE t."typeID" = m."typeID" AND t2."typeID" = m."materialTypeID" AND ap."typeID" = t."typeID" AND m."activityID" = 1
  ORDER BY t."typeID";

  CREATE OR REPLACE VIEW v_build_time AS
 SELECT invtypes."typeID" AS id,
    "industryActivity"."time"
   FROM "industryActivity",
    invtypes
  WHERE "industryActivity"."typeID" = invtypes."typeID" AND "industryActivity"."activityID" = 1;

  CREATE OR REPLACE VIEW v_buildable_fittings WITH (security_barrier=false) AS
 SELECT ship_fittings.build_id,
    ship_fittings.ship_id,
    ship_fittings.ship_name,
    ship_fittings.jita_buy,
    ship_fittings.qty,
    mt."typeID" AS id,
    ship_fittings.component,
    ship_fittings.component_cost,
    ship_fittings.component_qty,
    ship_fittings.build_cost,
    mt."metaGroupID" AS meta,
    ship_fittings.rollup,
    ship_fittings.user_id,
    0 AS bp_id
   FROM ship_fittings,
    "invMetaTypes" mt
  WHERE mt."typeID" = ship_fittings.component_id
  ORDER BY ship_fittings.component;

  CREATE OR REPLACE VIEW v_buildable_fittings_all AS
 SELECT ship_fittings.build_id,
    ship_fittings.ship_id,
    ship_fittings.ship_name,
    ship_fittings.jita_buy,
    ship_fittings.qty,
    ship_fittings.component_id AS id,
    ship_fittings.component,
    ship_fittings.component_cost,
    ship_fittings.component_qty,
    ship_fittings.build_cost,
    "industryActivityProducts"."activityID" AS meta,
    ship_fittings.rollup,
    ship_fittings.user_id,
    "industryActivityProducts"."typeID" AS bp_id
   FROM ship_fittings,
    "industryActivityProducts"
  WHERE "industryActivityProducts"."productTypeID" = ship_fittings.component_id
  ORDER BY ship_fittings.component;

  CREATE OR REPLACE VIEW v_count_fittings AS
 SELECT DISTINCT ship_fittings.build_id,
    ship_fittings.ship_id,
    ship_fittings.ship_name,
    ship_fittings.user_id,
    ship_fittings.contract_sell_price,
    ship_fittings.qty,
    ship_fittings.rollup,
    ship_fittings.jita_buy
   FROM ship_fittings;

   CREATE OR REPLACE VIEW v_datacore_requirements AS
 SELECT t."typeID" AS id,
    t2."typeName" AS datacore,
    m.quantity,
    m."materialTypeID" AS dc_id
   FROM invtypes t,
    "industryActivityMaterials" m,
    invtypes t2
  WHERE t."typeID" = m."typeID" AND m."materialTypeID" = t2."typeID" AND m."activityID" = 8
  ORDER BY t."typeName";

  CREATE OR REPLACE VIEW v_invent_pipeline_products AS
 SELECT DISTINCT invent_pipeline.product_name,
    invent_pipeline.user_id,
    invent_pipeline.runs,
    invent_pipeline.blueprint_id,
    invent_pipeline.status
   FROM invent_pipeline;

   CREATE OR REPLACE VIEW v_invent_time AS
 SELECT invtypes."typeID" AS id,
    "industryActivity"."time"
   FROM "industryActivity",
    invtypes
  WHERE "industryActivity"."typeID" = invtypes."typeID" AND "industryActivity"."activityID" = 8;

  CREATE OR REPLACE VIEW v_invention_product AS
 SELECT t."typeID" AS id,
    t2."typeName" AS t2_blueprint,
    p."productTypeID" AS t2_id
   FROM invtypes t,
    "industryActivityProducts" p,
    invtypes t2
  WHERE t."typeID" = p."typeID" AND p."productTypeID" = t2."typeID" AND p."activityID" = 8
  ORDER BY t2."typeName";

  CREATE OR REPLACE VIEW v_item_by_cat AS
 SELECT t."typeID" AS id,
    t."typeName" AS item,
    g."categoryID" AS category
   FROM invtypes t,
    invgroups g
  WHERE g."groupID" = t."groupID"
  ORDER BY t."typeName";

  CREATE OR REPLACE VIEW v_modules AS
 SELECT t."typeID" AS id,
    t."typeName" AS item,
    te."effectID" AS category
   FROM invtypes t,
    "dgmTypeEffects" te
  WHERE te."typeID" = t."typeID"
  ORDER BY t."typeName";

  CREATE OR REPLACE VIEW v_my_build_product AS
 SELECT assets_onhand.user_id,
    assets_onhand.product_id AS id,
    v_build_product.t2_blueprint,
    v_build_product.t2_id,
    assets_onhand.location_id,
    assets_onhand.qty
   FROM assets_onhand,
    v_build_product
  WHERE v_build_product.id = assets_onhand.product_id
  ORDER BY v_build_product.t2_blueprint;

  CREATE OR REPLACE VIEW v_my_invention_product AS
 SELECT assets_onhand.user_id,
    assets_onhand.product_id AS id,
    v_invention_product.t2_blueprint,
    v_invention_product.t2_id,
    assets_onhand.location_id,
    assets_onhand.qty
   FROM assets_onhand,
    v_invention_product
  WHERE v_invention_product.id = assets_onhand.product_id
  ORDER BY v_invention_product.t2_blueprint;

  CREATE OR REPLACE VIEW v_probability AS
 SELECT t."typeID" AS id,
    prob.probability
   FROM invtypes t,
    "industryActivityProbabilities" prob
  WHERE prob."typeID" = t."typeID" AND prob."activityID" = 8;

  CREATE OR REPLACE VIEW v_product AS
 SELECT t."typeID" AS id,
    p."productTypeID" AS t2_id
   FROM invtypes t,
    "industryActivityProducts" p,
    invtypes t2
  WHERE t."typeID" = p."typeID" AND p."productTypeID" = t2."typeID" AND p."activityID" = 1;

  CREATE OR REPLACE VIEW v_rigs AS
   SELECT t."typeID" AS id,
      t."typeName" AS item,
      ta."valueFloat" AS size
     FROM invtypes t,
      "dgmTypeEffects" te,
      "dgmTypeAttributes" ta
    WHERE te."typeID" = ta."typeID" AND ta."typeID" = t."typeID" AND te."effectID" = 2663 AND ta."attributeID" = 1547
    ORDER BY t."typeName";


    CREATE OR REPLACE VIEW v_ships AS
     SELECT t."typeID" AS id,
        t."typeName" AS ship
       FROM invtypes t,
        invgroups g,
        "invCategories" c
      WHERE g."groupID" = t."groupID" AND c."categoryID" = g."categoryID" AND c."categoryID" = 6
      ORDER BY t."typeName";

      CREATE OR REPLACE VIEW v_shipslots AS
 SELECT at."attributeID" AS id,
    ta."typeID" AS ship_id,
    ta."valueInt" AS valint,
    ta."valueFloat" AS valfloat
   FROM "dgmTypeAttributes" ta,
    "dgmAttributeTypes" at
  WHERE at."attributeID" = ta."attributeID";
