-- Name: assets_onhand_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.assets_onhand_id_seq
    START WITH 45333
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.assets_onhand_id_seq OWNER TO chris;

--
-- Name: assets_onhand; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.assets_onhand (
    id integer DEFAULT nextval('public.assets_onhand_id_seq'::regclass) NOT NULL,
    user_id integer,
    product_id integer,
    item_id character varying(100),
    location_flag character varying(100),
    location_type character varying(100),
    location_id character varying(100),
    qty integer,
    is_singleton boolean
);


ALTER TABLE public.assets_onhand OWNER TO chris;

--
-- Name: build_pipeline_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.build_pipeline_id_seq
    START WITH 7441
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.build_pipeline_id_seq OWNER TO chris;

--
-- Name: build_pipeline; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.build_pipeline (
    id integer DEFAULT nextval('public.build_pipeline_id_seq'::regclass) NOT NULL,
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
    material_vol double precision,
    portion_size integer,
    mat_eff double precision,
    time_eff double precision,
    eng_rig double precision,
    eng_role double precision
);


ALTER TABLE public.build_pipeline OWNER TO chris;

--
-- Name: build_pipeline_hx_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.build_pipeline_hx_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.build_pipeline_hx_id_seq OWNER TO chris;

--
-- Name: build_pipeline_hx; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.build_pipeline_hx (
    id integer DEFAULT nextval('public.build_pipeline_hx_id_seq'::regclass) NOT NULL,
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
    material_vol double precision,
    portion_size integer,
    mat_eff double precision,
    time_eff double precision,
    eng_rig double precision,
    eng_role double precision
);


ALTER TABLE public.build_pipeline_hx OWNER TO chris;


--
-- Name: eve_sso; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.eve_sso (
    id integer NOT NULL,
    client_id character varying(100),
    secret_key character varying(100),
    scope character varying(100)
);


ALTER TABLE public.eve_sso OWNER TO chris;

--
-- Name: forge_market_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.forge_market_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.forge_market_id_seq OWNER TO chris;

--
-- Name: forge_market; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.forge_market (
    id integer DEFAULT nextval('public.forge_market_id_seq'::regclass) NOT NULL,
    duration integer,
    is_buy_order boolean,
    issued timestamp without time zone,
    location_id character varying(100),
    min_volume integer,
    order_id character varying(100),
    price double precision,
    range character varying(100),
    system_id character varying(100),
    type_id character varying(100),
    volume_remain integer,
    volume_total integer
);


ALTER TABLE public.forge_market OWNER TO chris;


--
-- Name: invent_pipeline_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.invent_pipeline_id_seq
    START WITH 164
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.invent_pipeline_id_seq OWNER TO chris;

--
-- Name: invent_pipeline; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.invent_pipeline (
    id integer DEFAULT nextval('public.invent_pipeline_id_seq'::regclass) NOT NULL,
    user_id integer,
    product_id integer,
    blueprint_id integer,
    runs integer,
    product_name character varying(100),
    datacore_id integer,
    datacore_qty integer,
    datacore_cost double precision,
    datacore character varying(100),
    datacore_vol double precision,
    status integer
);


ALTER TABLE public.invent_pipeline OWNER TO chris;

--
-- Name: job_journal_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.job_journal_id_seq
    START WITH 135
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.job_journal_id_seq OWNER TO chris;

--
-- Name: job_journal; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.job_journal (
    id integer DEFAULT nextval('public.job_journal_id_seq'::regclass) NOT NULL,
    job_id character varying(100) NOT NULL,
    user_id integer,
    product_id integer,
    activity_id integer,
    facility_id character varying(100),
    station_id character varying(100),
    licensed_runs integer,
    runs integer,
    blueprint_location_id character varying(100),
    output_location_id character varying(100),
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    status character varying(50),
    job_cost double precision
);


ALTER TABLE public.job_journal OWNER TO chris;


--
-- Name: mining_calc_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.mining_calc_id_seq
    START WITH 14
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mining_calc_id_seq OWNER TO chris;

--
-- Name: mining_calc; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.mining_calc (
    id integer DEFAULT nextval('public.mining_calc_id_seq'::regclass) NOT NULL,
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
    asteroid4_id integer
);


ALTER TABLE public.mining_calc OWNER TO chris;


--
-- Name: ship_fittings_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.ship_fittings_id_seq
    START WITH 2442
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ship_fittings_id_seq OWNER TO chris;

--
-- Name: ship_fittings; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.ship_fittings (
    id integer DEFAULT nextval('public.ship_fittings_id_seq'::regclass) NOT NULL,
    build_id integer,
    user_id integer,
    ship_id integer,
    ship_name character varying(100),
    fitting_name character varying(100),
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
    rollup integer
);


ALTER TABLE public.ship_fittings OWNER TO chris;


--
-- Name: user_contracts_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.user_contracts_id_seq
    START WITH 19168
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_contracts_id_seq OWNER TO chris;

--
-- Name: user_contracts; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.user_contracts (
    id integer DEFAULT nextval('public.user_contracts_id_seq'::regclass) NOT NULL,
    user_id character varying(100),
    contract_id character varying(100),
    date_issued timestamp without time zone,
    date_expired timestamp without time zone,
    date_completed timestamp without time zone,
    date_accepted timestamp without time zone,
    for_corporation boolean,
    issue_corporation_id character varying(100),
    price double precision,
    status character varying(100),
    title character varying(100),
    duration integer,
    type character varying(100),
    build_cost double precision,
    availability character varying(100)
);


ALTER TABLE public.user_contracts OWNER TO chris;

--
-- Name: user_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.user_orders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_orders_id_seq OWNER TO chris;

--
-- Name: user_orders; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.user_orders (
    id integer DEFAULT nextval('public.user_orders_id_seq'::regclass) NOT NULL,
    user_id character varying(100),
    duration integer,
    escrow double precision,
    is_buy_order boolean,
    is_corporation boolean,
    issued timestamp without time zone,
    location_id character varying(100),
    min_volume integer,
    order_id character varying(100),
    price double precision,
    range character varying(100),
    region_id character varying(100),
    type_id character varying(100),
    volume_remain integer,
    volume_total integer,
    product_name character varying(100),
    build_cost double precision,
    build_runs integer
);


ALTER TABLE public.user_orders OWNER TO chris;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.users_id_seq
    START WITH 20
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO chris;

--
-- Name: users; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.users (
    id integer DEFAULT nextval('public.users_id_seq'::regclass) NOT NULL,
    character_id character varying(100),
    character_name character varying(100),
    refresh_token character varying(255),
    expiration timestamp without time zone,
    auth_code character varying(255),
    active boolean,
    last_logged_in timestamp without time zone,
    home_station_id character varying(100),
    structure_role_bonus double precision,
    default_bp_me double precision,
    corp_id character varying(100),
    default_bp_te double precision,
    structure_rig_bonus double precision
);


ALTER TABLE public.users OWNER TO chris;

--
-- Name: v_asteroid_groups; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_asteroid_groups AS
 SELECT DISTINCT "invGroups"."groupID" AS id,
    "invGroups"."groupName" AS "group"
   FROM public."invGroups"
  WHERE (("invGroups"."categoryID" = 25) AND ("invGroups"."groupID" <> 903))
  ORDER BY "invGroups"."groupID";


ALTER TABLE public.v_asteroid_groups OWNER TO chris;

--
-- Name: v_asteroids; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_asteroids AS
 SELECT "invTypes"."typeID" AS id,
    "invGroups"."groupID" AS group_id,
    "invTypes"."typeName" AS asteroid,
    "invTypes".volume AS vol,
    "invTypes"."portionSize" AS portion
   FROM public."invTypes",
    public."invGroups"
  WHERE (("invGroups"."groupID" = "invTypes"."groupID") AND ("invGroups"."categoryID" = 25) AND ("invGroups"."groupID" <> 903) AND ("invTypes"."portionSize" > 1))
  ORDER BY "invGroups"."groupID", "invTypes"."typeID";


ALTER TABLE public.v_asteroids OWNER TO chris;

--
-- Name: v_build_components; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_build_components AS
 SELECT t."typeID" AS id,
    t2."typeName" AS material,
    t2."typeID" AS material_id,
    m.quantity,
    t2.volume AS vol,
    t2."groupID" AS group_id
   FROM public."invTypes" t,
    public."invTypeMaterials" m,
    public."invTypes" t2
  WHERE ((m."typeID" = t."typeID") AND (t2."typeID" = m."materialTypeID"));


ALTER TABLE public.v_build_components OWNER TO chris;

--
-- Name: v_build_pipeline_products; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_build_pipeline_products AS
 SELECT DISTINCT build_pipeline.product_name,
    build_pipeline.user_id,
    build_pipeline.blueprint_id,
    build_pipeline.product_id,
    build_pipeline.runs,
    build_pipeline.jita_sell_price,
    build_pipeline.local_sell_price,
    build_pipeline.build_cost,
    build_pipeline.status,
    build_pipeline.portion_size,
    build_pipeline.eng_rig,
    build_pipeline.eng_role
   FROM public.build_pipeline;


ALTER TABLE public.v_build_pipeline_products OWNER TO chris;

--
-- Name: v_build_product; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_build_product AS
 SELECT t."typeID" AS id,
    t2."typeName" AS t2_blueprint,
    p."productTypeID" AS t2_id
   FROM public."invTypes" t,
    public."industryActivityProducts" p,
    public."invTypes" t2
  WHERE ((t."typeID" = p."typeID") AND (p."productTypeID" = t2."typeID") AND ((p."activityID" = 1) OR (p."activityID" = 11)))
  ORDER BY t2."typeName";


ALTER TABLE public.v_build_product OWNER TO chris;

--
-- Name: v_build_reactions; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_build_reactions AS
 SELECT t."typeID" AS id,
    t."typeName" AS material,
    t2."typeID" AS material_id,
    m.quantity,
    t2.volume AS vol,
    t2."groupID" AS group_id
   FROM public."invTypes" t,
    public."invTypeReactions" m,
    public."invTypes" t2
  WHERE ((m."typeID" = t."typeID") AND (t2."typeID" = m."reactionTypeID"));


ALTER TABLE public.v_build_reactions OWNER TO chris;

--
-- Name: v_build_requirements; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_build_requirements AS
 SELECT t."typeID" AS id,
    t2."typeName" AS material,
    t2."typeID" AS material_id,
    t2."groupID" AS group_id,
    m.quantity AS qty,
    ap."productTypeID" AS product_id,
    t2.volume AS vol,
    t2."portionSize" AS portion_size
   FROM public."industryActivityMaterials" m,
    public."invTypes" t,
    public."invTypes" t2,
    public."industryActivityProducts" ap
  WHERE ((t."typeID" = m."typeID") AND (t2."typeID" = m."materialTypeID") AND (ap."typeID" = t."typeID") AND ((m."activityID" = 1) OR (m."activityID" = 11)))
  ORDER BY t."typeID";


ALTER TABLE public.v_build_requirements OWNER TO chris;

--
-- Name: v_build_time; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_build_time AS
 SELECT "invTypes"."typeID" AS id,
    "industryActivity"."time"
   FROM public."industryActivity",
    public."invTypes"
  WHERE (("industryActivity"."typeID" = "invTypes"."typeID") AND (("industryActivity"."activityID" = 1) OR ("industryActivity"."activityID" = 11)));


ALTER TABLE public.v_build_time OWNER TO chris;

--
-- Name: v_buildable_fittings; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_buildable_fittings AS
 SELECT ship_fittings.build_id,
    ship_fittings.ship_id,
    ship_fittings.ship_name,
    ship_fittings.fitting_name,
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
   FROM public.ship_fittings,
    public."invMetaTypes" mt
  WHERE (mt."typeID" = ship_fittings.component_id)
  ORDER BY ship_fittings.component;


ALTER TABLE public.v_buildable_fittings OWNER TO chris;

--
-- Name: v_buildable_fittings_all; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_buildable_fittings_all AS
 SELECT ship_fittings.build_id,
    ship_fittings.ship_id,
    ship_fittings.ship_name,
    ship_fittings.fitting_name,
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
   FROM public.ship_fittings,
    public."industryActivityProducts"
  WHERE ("industryActivityProducts"."productTypeID" = ship_fittings.component_id)
  ORDER BY ship_fittings.component;


ALTER TABLE public.v_buildable_fittings_all OWNER TO chris;

--
-- Name: v_count_fittings; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_count_fittings AS
 SELECT DISTINCT ship_fittings.build_id,
    ship_fittings.ship_id,
    ship_fittings.ship_name,
    ship_fittings.fitting_name,
    ship_fittings.user_id,
    ship_fittings.contract_sell_price,
    ship_fittings.qty,
    ship_fittings.rollup,
    ship_fittings.jita_buy
   FROM public.ship_fittings;


ALTER TABLE public.v_count_fittings OWNER TO chris;

--
-- Name: v_datacore_requirements; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_datacore_requirements AS
 SELECT t."typeID" AS id,
    t2."typeName" AS datacore,
    m.quantity,
    m."materialTypeID" AS dc_id,
    t2.volume AS vol
   FROM public."invTypes" t,
    public."industryActivityMaterials" m,
    public."invTypes" t2
  WHERE ((t."typeID" = m."typeID") AND (m."materialTypeID" = t2."typeID") AND (m."activityID" = 8))
  ORDER BY t."typeName";


ALTER TABLE public.v_datacore_requirements OWNER TO chris;

--
-- Name: v_invent_pipeline_products; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_invent_pipeline_products AS
 SELECT DISTINCT invent_pipeline.product_name,
    invent_pipeline.user_id,
    invent_pipeline.runs,
    invent_pipeline.blueprint_id,
    invent_pipeline.status
   FROM public.invent_pipeline;


ALTER TABLE public.v_invent_pipeline_products OWNER TO chris;

--
-- Name: v_invent_time; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_invent_time AS
 SELECT "invTypes"."typeID" AS id,
    "industryActivity"."time"
   FROM public."industryActivity",
    public."invTypes"
  WHERE (("industryActivity"."typeID" = "invTypes"."typeID") AND ("industryActivity"."activityID" = 8));


ALTER TABLE public.v_invent_time OWNER TO chris;

--
-- Name: v_invention_product; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_invention_product AS
 SELECT t."typeID" AS id,
    t2."typeName" AS t2_blueprint,
    p."productTypeID" AS t2_id
   FROM public."invTypes" t,
    public."industryActivityProducts" p,
    public."invTypes" t2
  WHERE ((t."typeID" = p."typeID") AND (p."productTypeID" = t2."typeID") AND (p."activityID" = 8))
  ORDER BY t2."typeName";


ALTER TABLE public.v_invention_product OWNER TO chris;

--
-- Name: v_item_by_cat; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_item_by_cat AS
 SELECT t."typeID" AS id,
    t."typeName" AS item,
    g."categoryID" AS category
   FROM public."invTypes" t,
    public."invGroups" g
  WHERE (g."groupID" = t."groupID")
  ORDER BY t."typeName";


ALTER TABLE public.v_item_by_cat OWNER TO chris;

--
-- Name: v_modules; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_modules AS
 SELECT t."typeID" AS id,
    t."typeName" AS item,
    te."effectID" AS category
   FROM public."invTypes" t,
    public."dgmTypeEffects" te
  WHERE (te."typeID" = t."typeID")
  ORDER BY t."typeName";


ALTER TABLE public.v_modules OWNER TO chris;

--
-- Name: v_my_build_product; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_my_build_product AS
 SELECT a.user_id,
    a.product_id AS id,
    t2."typeName" AS t2_blueprint,
    p."productTypeID" AS t2_id,
    a.location_id,
    a.qty
   FROM public.assets_onhand a,
    public."industryActivityProducts" p,
    public."invTypes" t2
  WHERE ((a.product_id = p."typeID") AND (p."productTypeID" = t2."typeID"))
  ORDER BY t2."typeName";


ALTER TABLE public.v_my_build_product OWNER TO chris;

--
-- Name: v_my_build_product1; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_my_build_product1 AS
 SELECT a.user_id,
    a.product_id AS id,
    t2."typeName" AS t2_blueprint,
    p."productTypeID" AS t2_id,
    a.location_id,
    a.qty
   FROM public.assets_onhand a,
    public."industryActivityProducts" p,
    public."invTypes" t2
  WHERE ((a.product_id = p."typeID") AND (p."productTypeID" = t2."typeID"))
  ORDER BY t2."typeName";


ALTER TABLE public.v_my_build_product1 OWNER TO chris;

--
-- Name: v_my_invention_product; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_my_invention_product AS
 SELECT assets_onhand.user_id,
    assets_onhand.product_id AS id,
    v_invention_product.t2_blueprint,
    v_invention_product.t2_id,
    assets_onhand.location_id,
    assets_onhand.qty
   FROM public.assets_onhand,
    public.v_invention_product
  WHERE (v_invention_product.id = assets_onhand.product_id)
  ORDER BY v_invention_product.t2_blueprint;


ALTER TABLE public.v_my_invention_product OWNER TO chris;

--
-- Name: v_probability; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_probability AS
 SELECT t."typeID" AS id,
    prob.probability
   FROM public."invTypes" t,
    public."industryActivityProbabilities" prob
  WHERE ((prob."typeID" = t."typeID") AND (prob."activityID" = 8));


ALTER TABLE public.v_probability OWNER TO chris;

--
-- Name: v_product; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_product AS
 SELECT t."typeID" AS id,
    p."productTypeID" AS t2_id
   FROM public."invTypes" t,
    public."industryActivityProducts" p,
    public."invTypes" t2
  WHERE ((t."typeID" = p."typeID") AND (p."productTypeID" = t2."typeID") AND (p."activityID" = 1));


ALTER TABLE public.v_product OWNER TO chris;

--
-- Name: wallet_journal_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.wallet_journal_id_seq
    START WITH 3668
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wallet_journal_id_seq OWNER TO chris;

--
-- Name: wallet_journal; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.wallet_journal (
    id integer DEFAULT nextval('public.wallet_journal_id_seq'::regclass) NOT NULL,
    user_id character varying(100),
    amount double precision,
    date_transaction timestamp without time zone,
    transaction_id character varying(100),
    ref_type character varying(100)
);


ALTER TABLE public.wallet_journal OWNER TO chris;

--
-- Name: wallet_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: chris
--

CREATE SEQUENCE public.wallet_transactions_id_seq
    START WITH 1245
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wallet_transactions_id_seq OWNER TO chris;

--
-- Name: wallet_transactions; Type: TABLE; Schema: public; Owner: chris
--

CREATE TABLE public.wallet_transactions (
    id integer DEFAULT nextval('public.wallet_transactions_id_seq'::regclass) NOT NULL,
    user_id character varying(100),
    amount double precision,
    date_transaction timestamp without time zone,
    transaction_id character varying(100),
    client_id character varying(100),
    location_id character varying(100),
    qty integer,
    product_id integer
);


ALTER TABLE public.wallet_transactions OWNER TO chris;

--
-- Name: v_purchases; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_purchases AS
 SELECT wallet_transactions.id,
    wallet_transactions.user_id,
    "invTypes"."typeID" AS type_id,
    "invTypes"."typeName" AS product_name,
    wallet_transactions.qty,
    wallet_transactions.amount,
    wallet_transactions.date_transaction
   FROM public.wallet_journal,
    public.wallet_transactions,
    public."invTypes"
  WHERE (((wallet_journal.user_id)::text = (wallet_transactions.user_id)::text) AND (wallet_journal.date_transaction = wallet_transactions.date_transaction) AND (wallet_journal.date_transaction = wallet_transactions.date_transaction) AND ("invTypes"."typeID" = wallet_transactions.product_id) AND ((wallet_journal.ref_type)::text = 'market_escrow'::text))
  ORDER BY wallet_transactions.date_transaction, "invTypes"."typeName";


ALTER TABLE public.v_purchases OWNER TO chris;

--
-- Name: v_rigs; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_rigs AS
 SELECT t."typeID" AS id,
    t."typeName" AS item,
    ta."valueFloat" AS size
   FROM public."invTypes" t,
    public."dgmTypeEffects" te,
    public."dgmTypeAttributes" ta
  WHERE ((te."typeID" = ta."typeID") AND (ta."typeID" = t."typeID") AND (te."effectID" = 2663) AND (ta."attributeID" = 1547))
  ORDER BY t."typeName";


ALTER TABLE public.v_rigs OWNER TO chris;

--
-- Name: v_sales; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_sales AS
 SELECT wallet_transactions.id,
    wallet_transactions.user_id,
    "invTypes"."typeID" AS type_id,
    "invTypes"."typeName" AS product_name,
    wallet_transactions.qty,
    wallet_transactions.amount,
    wallet_transactions.date_transaction
   FROM public.wallet_journal,
    public.wallet_transactions,
    public."invTypes"
  WHERE (((wallet_journal.user_id)::text = (wallet_transactions.user_id)::text) AND (wallet_journal.date_transaction = wallet_transactions.date_transaction) AND (wallet_journal.date_transaction = wallet_transactions.date_transaction) AND ("invTypes"."typeID" = wallet_transactions.product_id) AND ((wallet_journal.ref_type)::text = 'market_transaction'::text))
  ORDER BY wallet_transactions.date_transaction, "invTypes"."typeName";


ALTER TABLE public.v_sales OWNER TO chris;

--
-- Name: v_ships; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_ships AS
 SELECT t."typeID" AS id,
    t."typeName" AS ship
   FROM public."invTypes" t,
    public."invGroups" g,
    public."invCategories" c
  WHERE ((g."groupID" = t."groupID") AND (c."categoryID" = g."categoryID") AND (c."categoryID" = 6))
  ORDER BY t."typeName";


ALTER TABLE public.v_ships OWNER TO chris;

--
-- Name: v_shipslots; Type: VIEW; Schema: public; Owner: chris
--

CREATE VIEW public.v_shipslots AS
 SELECT at."attributeID" AS id,
    ta."typeID" AS ship_id,
    ta."valueInt" AS valint,
    ta."valueFloat" AS valfloat
   FROM public."dgmTypeAttributes" ta,
    public."dgmAttributeTypes" at
  WHERE (at."attributeID" = ta."attributeID");


ALTER TABLE public.v_shipslots OWNER TO chris;


--
-- Name: assets_onhand b_assets_oh_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.assets_onhand
    ADD CONSTRAINT b_assets_oh_pkey PRIMARY KEY (id);


--
-- Name: forge_market b_forge_market_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.forge_market
    ADD CONSTRAINT b_forge_market_pkey PRIMARY KEY (id);


--
-- Name: job_journal b_job_journal_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.job_journal
    ADD CONSTRAINT b_job_journal_pkey PRIMARY KEY (job_id);


--
-- Name: mining_calc b_mining_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.mining_calc
    ADD CONSTRAINT b_mining_pkey PRIMARY KEY (id);


--
-- Name: build_pipeline_hx b_pipeline_hx_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.build_pipeline_hx
    ADD CONSTRAINT b_pipeline_hx_pkey PRIMARY KEY (id);


--
-- Name: build_pipeline b_pipeline_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.build_pipeline
    ADD CONSTRAINT b_pipeline_pkey PRIMARY KEY (id);


--
-- Name: ship_fittings b_shipfittings_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.ship_fittings
    ADD CONSTRAINT b_shipfittings_pkey PRIMARY KEY (id);



--
-- Name: eve_sso evesso_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.eve_sso
    ADD CONSTRAINT evesso_pkey PRIMARY KEY (id);


--
-- Name: invent_pipeline i_pipeline_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.invent_pipeline
    ADD CONSTRAINT i_pipeline_pkey PRIMARY KEY (id);


--
-- Name: user_contracts user_contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.user_contracts
    ADD CONSTRAINT user_contracts_pkey PRIMARY KEY (id);


--
-- Name: user_orders user_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.user_orders
    ADD CONSTRAINT user_orders_pkey PRIMARY KEY (id);


--
-- Name: users user_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: wallet_journal wallet_journal_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.wallet_journal
    ADD CONSTRAINT wallet_journal_pkey PRIMARY KEY (id);


--
-- Name: wallet_transactions wallet_transaction_pkey; Type: CONSTRAINT; Schema: public; Owner: chris
--

ALTER TABLE ONLY public.wallet_transactions
    ADD CONSTRAINT wallet_transaction_pkey PRIMARY KEY (id);



--
-- Name: industryActivityMaterials_idx1; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "industryActivityMaterials_idx1" ON public."industryActivityMaterials" USING btree ("typeID", "activityID");


--
-- Name: industryActivitySkills_idx1; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "industryActivitySkills_idx1" ON public."industryActivitySkills" USING btree ("typeID", "activityID");


--
-- Name: invUniqueNames_IX_GroupName; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "invUniqueNames_IX_GroupName" ON public."invUniqueNames" USING btree ("groupID", "itemName");


--
-- Name: items_IX_OwnerLocation; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "items_IX_OwnerLocation" ON public."invItems" USING btree ("ownerID", "locationID");


--
-- Name: ix_agtAgents_corporationID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_agtAgents_corporationID" ON public."agtAgents" USING btree ("corporationID");


--
-- Name: ix_agtAgents_locationID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_agtAgents_locationID" ON public."agtAgents" USING btree ("locationID");


--
-- Name: ix_agtResearchAgents_typeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_agtResearchAgents_typeID" ON public."agtResearchAgents" USING btree ("typeID");


--
-- Name: ix_assets_onhand_product_id; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX ix_assets_onhand_product_id ON public.assets_onhand USING btree (product_id);


--
-- Name: ix_build_pipeline_group_id; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX ix_build_pipeline_group_id ON public.build_pipeline USING btree (group_id);


--
-- Name: ix_build_pipeline_material_id; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX ix_build_pipeline_material_id ON public.build_pipeline USING btree (material_id);


--
-- Name: ix_dgmAttributeTypes_typeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_dgmAttributeTypes_typeID" ON public."dgmAttributeTypes" USING btree ("attributeID");


--
-- Name: ix_dgmTypeAttributes_attributeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_dgmTypeAttributes_attributeID" ON public."dgmTypeAttributes" USING btree ("attributeID");


--
-- Name: ix_dgmTypeAttributes_typeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_dgmTypeAttributes_typeID" ON public."dgmTypeAttributes" USING btree ("typeID");


--
-- Name: ix_dgmTypeAttributes_valueFloat; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_dgmTypeAttributes_valueFloat" ON public."dgmTypeAttributes" USING btree ("valueFloat");


--
-- Name: ix_dgmTypeAttributes_valueInt; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_dgmTypeAttributes_valueInt" ON public."dgmTypeAttributes" USING btree ("valueInt");


--
-- Name: ix_dgmTypeEffects_effectID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_dgmTypeEffects_effectID" ON public."dgmTypeEffects" USING btree ("effectID");


--
-- Name: ix_dgmTypeEffects_typeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_dgmTypeEffects_typeID" ON public."dgmTypeEffects" USING btree ("typeID");


--
-- Name: ix_forge_market_type_id; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX ix_forge_market_type_id ON public.forge_market USING btree (type_id);


--
-- Name: ix_industryActivityMaterials_typeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_industryActivityMaterials_typeID" ON public."industryActivityMaterials" USING btree ("typeID");


--
-- Name: ix_industryActivityProbabilities_productTypeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_industryActivityProbabilities_productTypeID" ON public."industryActivityProbabilities" USING btree ("productTypeID");


--
-- Name: ix_industryActivityProbabilities_typeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_industryActivityProbabilities_typeID" ON public."industryActivityProbabilities" USING btree ("typeID");


--
-- Name: ix_industryActivityProducts_productTypeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_industryActivityProducts_productTypeID" ON public."industryActivityProducts" USING btree ("productTypeID");


--
-- Name: ix_industryActivityProducts_typeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_industryActivityProducts_typeID" ON public."industryActivityProducts" USING btree ("typeID");


--
-- Name: ix_industryActivityRaces_productTypeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_industryActivityRaces_productTypeID" ON public."industryActivityRaces" USING btree ("productTypeID");


--
-- Name: ix_industryActivityRaces_typeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_industryActivityRaces_typeID" ON public."industryActivityRaces" USING btree ("typeID");


--
-- Name: ix_industryActivitySkills_skillID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_industryActivitySkills_skillID" ON public."industryActivitySkills" USING btree ("skillID");


--
-- Name: ix_industryActivitySkills_typeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_industryActivitySkills_typeID" ON public."industryActivitySkills" USING btree ("typeID");


--
-- Name: ix_industryActivity_activityID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_industryActivity_activityID" ON public."industryActivity" USING btree ("activityID");


--
-- Name: ix_invGroups_categoryID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_invGroups_categoryID" ON public."invGroups" USING btree ("categoryID");


--
-- Name: ix_invItems_locationID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_invItems_locationID" ON public."invItems" USING btree ("locationID");


--
-- Name: ix_invTypes_groupID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_invTypes_groupID" ON public."invTypes" USING btree ("groupID");


--
-- Name: ix_invTypes_typeID; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX "ix_invTypes_typeID" ON public."invTypes" USING btree ("typeID");


--
-- Name: ix_ship_fittings_component_id; Type: INDEX; Schema: public; Owner: chris
--

CREATE INDEX ix_ship_fittings_component_id ON public.ship_fittings USING btree (component_id);

