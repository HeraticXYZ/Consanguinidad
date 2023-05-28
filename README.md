# Consanguinidad
Consanguinity dispensation data analysis.

In the past, when closely related individuals sought marriage in a Catholic church, a dispensation (exemption) letter would be written to explain the ancestors they shared and give a descending genealogy for each of them, and to pardon them for the Catholic marital impediment of marriage within the fourth degree (3rd cousins or closer). These letters prove invaluable as genealogical resources. However, these letters are very often lost. The information they contain would be summarized in Catholic marriage records as numerical relations of consanguinity (e.g. "second with third grade", which means first cousin once removed).

Without the dispensation letters detailing the names and descendants of a couple's shared ancestors, we are left with numerical descriptions of their genealogical relationship. These descriptions (hereon referred to as "grades" or "degrees") are still quite valuable for the reconstruction of family pedigrees. Let us consider a simple example:

![segundo grado snip 1](https://user-images.githubusercontent.com/54190606/162840928-73730833-f7c8-4c74-9980-ce7f5efb9da5.PNG)

![segundo grado fuente snip](https://user-images.githubusercontent.com/54190606/162840885-5774825b-ad76-4fe3-8978-327ea3b96621.jpg)

In this example, a couple was married in 1869 in the town of Yabucoa, Puerto Rico, and received a dispensation of second grade of consanguinity. Serapio and Juliana's parents are given in the marriage document: Roberto Ramos and Facunda Delgado, and José Dolores Ramos and Ramona Aponte..

The degree (number) of consanguinity reflects the number of generations that have elapsed since the couple's shared ancestor(s). In this case, second grade means that Serapio and Juliana are both two generations below their shared ancestor(s). That is to say, Serapio and Juliana share a set of grandparents.

Without knowledge of who their grandparents are, we are left to speculate the nature of their blood relation. Generally, surnames are the biggest clues for where a shared ancestor might reside on a pedigree. In this case, Serapio and Juliana share the surname "Ramos", and we may infer that their fathers Roberto Ramos and José Dolores Ramos were brothers. This is, in fact, the case, as shown in the following figure.

![segundo grado snip 2](https://user-images.githubusercontent.com/54190606/162841265-7d48ef79-5971-43b4-906f-bf65caaeabf6.PNG)

More often than not, though, the degree of consanguinity between a couple takes on a more complex form, e.g. second with third grade, fourth grade, second and two of fourth grade, etc. As long as there is enough contextual data to construct a partial pedigree to reach these generations, one can use these dispensation data to reconstruct family histories without direct documentation of the individuals involved. For example, it is not necessary to find a document explicitly stating who Roberto Ramos's parents were because we are able to infer it from the dispensation data of his son Serapio.

Consanguinity analysis has been used by many genealogists to form conclusions about historical pedigrees. These analyses are performed by hand using diagrams and logical reasoning. However, as the degrees of relation become more distant, contextual information becomes sparse, and more dispensations must be considered simultaneously, this reasoning process becomes intractable by hand.

This program is designed to facilitate the analysis of multiple dispensations in these difficult cases. It does so by searching a GEDCOM formatted family tree file for given families, crawling their pedigress to construct hypothesis sets, and using cross-elimination to whittle down existing sets into useful conclusions. It also handles dispensational errors by pointing them out as soon as they are discovered. This happens either when a hypothesis set is reduced to zero (or below its token count), or when the known grades drawn from the GEDCOM contradict the grades given in the dispensation.
