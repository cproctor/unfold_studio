Unfold studio: supporting critical literacies of text and code

Critical
literacies of
text and code

Chris Proctor and Paulo Blikstein
Graduate School of Education, Stanford University, Palo Alto, California, USA

Abstract
Purpose – This research aims to explore how textual literacy and computational literacy can support each
other and combine to create literacies with new critical possibilities. It describes the development of a Web
application for interactive storytelling and analyzes how its use in a high-school classroom supported new
rhetorical techniques and critical analysis of gender and race.
Design/methodology/approach – Three iterations of design-based research were used to develop a
Web application for interactive storytelling, which combines writing with programming. A two-week study in
a high-school sociology class was conducted to analyze how the Web application's textual and computational
affordances support rhetorical strategies, which in turn support identity authorship and critical possibilities.
Findings – The results include a Web application for interactive storytelling and an analytical framework
for analyzing how affordances of digital media can support literacy practices with unique critical possibilities.
The ﬁnal study showed how interactive stories can function as critical discourse models, simulations of social
realities which support analysis of phenomena such as social positioning and the use of power.
Originality/value – Previous work has insufﬁciently spanned the ﬁelds of learning sciences and literacies,
respectively emphasizing the mechanisms and the content of literacy practices. In focusing a design-based
approach on critical awareness of identity, power and privilege, this research develops tools and theory for
supporting critical computational literacies. This research envisions a literacy-based approach to K-12
computer science which could contribute to liberatory education.

Keywords Critical literacy, Computational thinking, Literacy, Design-based research,
Computer science education, Computational literacy, Multiliteracies, K-12 computer science education
Paper type Research paper

Introduction
Literacy is about much more than learning to read and write. The practices which emerge
within networks of people and texts often have prosaic goals such as conveying messages,
documenting agreements and establishing authority, but they can profoundly reshape
participants’ cognition, identity practices and social relationships. Ong (2013) argues that
privileged access to reading and writing led to the emergence of new social roles high in the
status hierarchy, and that widespread literacy in a society “restructures consciousness”
(p. 77) by synchronizing frames of reference such as dates, facts and perspectives on the
world. In addition to supporting practices which deﬁne social roles and relationships,
Scribner and Cole (1978) found that reading and writing were associated with changes in
individual cognition such as improved abstract communication, memory and language
analysis skills (pp. 27-29). It is not necessary to argue for a direct causal link between
This research was supported by a grant from TELOS, Technology for Equity in Learning
Opportunities, by Stanford's Transformative Learning Technologies Lab, and by the Lemann Center
for Entrepreneurship and Educational Innovation in Brazil. The authors are deeply grateful to the
teachers and students with whom they conducted this research, and to the colleagues who have read
drafts of this article.

reading and writing and cognitive change, rather they may be seen as tools which have the
potential to spur a different developmental path for the individual and for the society
(Vygotsky, 1980).
Societies all over the world are increasingly becoming reliant on digital media, sometimes
in place of print text. Digital media functions differently from print text (Murray, 2017), so
we should expect digital literacies to function differently from print literacies. The designers
and technologists who invented personal computing were inspired by not just by
technological possibilities but also the possibility of new ways of living (Markoff, 2005).
Engelbart (1962) pursued augmented cognition through bootstrapping, a reciprocal process
by which technological advances allow new forms of cooperation and collaboration, which
enable further technological advances. Interfaces such as virtual reality and ubiquitous
mobile computing present not just new information channels but also “material exteriority”
(Hansen and Hayles, 2000), extensions and transformations of the body which redeﬁne the
subjectivities we may inhabit (Haraway, 2006; Lanier, 2010). Nelson's (1974) development of
hypertext was motivated by the possibility of new social, political and economic
arrangement. In contrast to the view of computers as primarily information-processing
machines, we argue that personal computing and the internet have always functioned as
technologies of literacy, making possible networks of humans and computers whose
practices transform cognition, identity practices and social relations.
Educators who understand learning as situated in contexts of people, spaces, tools, ideas
and purposes (Collins and Greeno, 2011) recognize the importance of bringing students into
communities of practice which engage with media in discipline-speciﬁc ways. They also
recognize the potential of new media to support the development of new cognitive and social
structures (Pea, 1985). One goal of this article is to bring together two distinct research
communities concerned with pedagogy, literacy and new media. The ﬁrst includes learning
scientists interested in how computers can support thinking and learning. The second
includes scholars of critical multiliteracies interested in how the same literacy practices
which can be so empowering also reproduce oppressive subjectivities and power
hierarchies, and in strategies for resisting and subverting them. The spread of computation
into all aspects of our lives, and the growing awareness that “Silicon Valley is not your
friend” (Cohen, 2017), makes it urgent that we integrate these two perspectives into an
understanding of critical computational literacies.
The learning sciences are concerned with the mechanisms by which people think and
learn with technology, individually and as participants in larger systems (Bransford et al.,
2000; Nathan and Wagner Alibali, 2010). Building on early socio-cultural theory, the
learning sciences have produced functional accounts of literacy (diSessa, 2001), as well as
complementary constructs, describing how communities think and learn through
interaction with media. These include distributed cognition (Cole and Engeström, 1993; Pea,
1993), activity theory and ﬁgured worlds (Holland et al., 2001). Within these theoretical
frames, design-based research (The Design-Based Research Collective, 2003; Bang and
Vossoughi, 2016) develops new technologies to understand and improve learning. These
include Papert's Logo (1980); diSessa (2000) and more recent computational media
(Sipitakiat, Blikstein, and Cavallo, 2004; Barab et al., 2005; Resnick et al., 2009).
A second research community on literacy pedagogy is focused on multiliteracies (New
London Group, 1996), a term which draws attention to “the multiplicity of communication
channels and media, and the increasing saliency of cultural and linguistic diversity” (p. 63).
Multiliteracies stands in a ﬁgure-ground relationship with the learning sciences approach to
literacies, emphasizing sociocultural issues of identity, voice, positionality and power.
Bringing attention to the ways dominant literacies also marginalize and disempower

demands taking a critical stance. Freire's (1968) political activism teaching the poor to read
was grounded in a recognition that text-mediated thought was responsible for constituting
them as passive subjects incapable of action. Learning to read the wor(l)d means
participating in social meaning-making instead of taking meaning as given, realizing that
the present world is constituted in certain ways and could have been different, and working
toward more just and inclusive futures. (When the term critical is used in this article, it is in
this sense.) In addition to contesting the hegemony of dominant literacies, critical
multiliteracies aim to re-value marginalized literacies as legitimate meaning-making
processes in and out of school (Paris, 2011; Morrell, 2015).
These two traditions have not been sufﬁciently in dialogue with one another,
respectively emphasizing the mechanisms and the content of literacy practices (Bang et al.,
2007; Vossoughi and Gutiérrez, 2016). As educators and practitioners within both textual
and computational literacy spaces, the authors are interested in studying the material and
critical possibilities of textual-computational multiliteracy. This research adopts the
methodology of participatory design research (The Design-Based Research Collective, 2003;
Anderson and Shattuck, 2012; Bang and Vossoughi, 2016), working iteratively with
adolescents to design and build a Web application that supports critical practices, drawing
on both writing and programming and collaborating with participants to interpret the
results. The starting point is the existing medium of interactive storytelling, which has
the affordances of both writing and programming and a history of critical resistance to the
sexism, racism and heteronormativity common in mainstream video games (Anthropy,
2012). The research questions guiding these studies are:
RQ1. What kind of medium and pedagogy might support textual-computational
multiliteracy?
RQ2. What practices might emerge in such a textual-computational multiliteracy space?
RQ3. How might such practices support critical awareness and resistance to racism,
sexism and other oppressive ideologies?
This article is structured around multiple iterations of design-based research developing a
Web application for interactive storytelling called Unfold Studio. The next section grounds
this research in existing literature and develops a conceptual framework for tracing how the
affordances of computational media support different rhetorical practices, producing
different meanings and identities and ultimately the possibility of critical activism. Then
this framework is used to analyze the iterative development of Unfold Studio, a Web
application for interactive storytelling. Finally, the article reports on an interactive
storytelling workshop which demonstrated that interactive storytelling can effectively
support critical textual-computational literacy. The article concludes with a discussion of
how these results contribute to theory and pedagogical practice.
Background
Literacy spaces
This article considers literacy to be a particular form of situated learning (Collins and
Greeno, 2011) in which a network of actors collaborate to do semiotic work. Actors may
include people, texts, computers, objects, ideas: anything which engages in meaningmaking, or which represents, interprets or mediates meaning, or which is marked as
meaningful. The abstract term actors is used so the deﬁnition can include conventional
communities reading and writing texts as well as scenarios where it is harder to distinguish
between the authors and the media. In computational literacy spaces, computers function as
semiotic media but may also introduce new ideas, engage in interpretation and author their
own identities. Computer programs are texts written by programmers, but given the right
environment, they can also function as authors, interlocutors or as interfaces mediating
readings of other texts. Chatbots, online avatars and news feeds have complex relationships
with the people who designed them, who control them and whom they purport to represent.
The question of agency is urgent, but not easy to answer.
Gee's (1990) term literacy space is used as a near synonym for literacy community or
ﬁgured world (Holland et al., 2001), following his rationale that it is unproductive to try to
deﬁne the membership boundaries of a literacy community. Would-be participants may be
excluded, while others may become implicated in a literacy space without their consent. A
literacy space is similar to a Discourse (Gee, 1990) or an ideology, although the latter two tend
to be larger networks with longer histories, so that participants are less able to transform
meanings within them. For example, Reyes (2017) documents how students within a school
literacy space in the USA were able to contest local stereotypes about what it means to be
Asian and author new identities for themselves, but they had to work within more
widespread ideologies about Asianness, Whiteness and legitimacy.
What kinds of interactions qualify as semiotic work? First, transforming old
meanings into new ones. Holland et al. (2001) describe a process of “symbolic
bootstrapping” (p. 38) or “heuristic development” (p. 40) by which actors take up
external tools (or ideas or symbols), use them, internalize them as part of their
developmental histories and thereby render their environments useful or meaningful in
new ways. The pattern for this process is Vygotsky's (1980) account of how people
acquire language and build concepts. For Holland et al., Bakhtin's (1981) heteroglossia –
the recursive composition of meaning from prior meanings – runs parallel to the
Vygotskian process of tool and concept construction. A point Vygotsky, Bakhtin and
Holland et al. emphasize is that the generation of new meanings is grounded in and
constrained by existing materials which always have histories. Each participant acts
from a history of participation which encodes the meanings of other actors, and so
continued participation sustains the historical meanings of the system.
The meanings of selves within literacy spaces develop via the same process. This article
uses the term identity to denote a model of selfhood one authors and occupies in a literacy
space, which exists at the interface “between intimate discourses, inner speaking, and bodily
practices formed in the past and the discourses and practices to which people are exposed,
willingly or not, in the present” (Holland et al., 2001, p. 32). Drawing again on Bakhtin's
dialogic self, Holland et al. describe identity as the negotiated meeting place of
unconstrained inner speech and an external subject position made available by social
meanings. The subject position speciﬁes the terms by which one is addressable and by
which one will answer.
What we call identities remain dependent upon social relations and material conditions. If these
relations and material conditions change, they must be 'answered,' and old 'answers' about who
one is may be undone (Holland et al., 1998, p. 189).

Analytical framework
This article's research questions contain an implicit chain of hypotheses:
 that the perceived affordances of a computational medium could shape the
rhetorical practices for which it is used;
that these practices could shape the meanings and identities which are thereby
enacted; and
that these meanings and identities could open possibilities for critical understanding
and activism.

This paper's analysis follows a four-layer analytical framework aligned with these
hypotheses: affordances, rhetoric, ﬁgured meanings and critical possibilities. Similar to
Brooke's (2009) framework for analyzing digital rhetoric at the levels of code, practice and
culture, each level permits analysis of the literacy space at a different scale.
The following subsections address each layer in turn, grounding its approach in prior
literature and explaining how it is operationalized in this research. It may appear
anachronistic to present this framework here, as its form emerged during the iterative
design-based research described in the next section, and it was formalized during iterative
rounds of grounded theory-based open coding (Charmaz, 1996) described in the subsequent
section. However, starting with the framework allows for a more intuitive organization of
the results which follow.
Aﬀordances. The development of a literacy medium can be analyzed in terms of its
affordances, or the ways it can be used to create meaning. The primary form of meaningmaking considered by this research is authors composing texts to shape the experiences of
readers. A second form of meaning-making, important to the critical possibilities of literacy,
is the way texts can open new possibilities for future authorship. Norman (1999)
distinguishes between affordances and perceived affordances – between the actionable
properties of an object and those perceived as such by a user. When considering media
which support literacy, this means distinguishing between the myriad ways a medium could
potentially be taken up in meaning-making, and the subset authors perceive as likely to be
recognized by an audience, within the context of the Web application interface. Therefore,
this article analyzes the perceived affordances of media through instances of their use.
The two media with which this article is most concerned, i.e. text and code, function
differently in supporting meaning-making and therefore offer different affordances.
Although in practice literacies are multi- and trans- (New London Group, 1996; Thomas
et al., 2007), there is value in distinguishing how reading a text differs from playing a
computational artifact such as a game or an interactive map (Aarseth, 1997). One essential
mechanism of text is representation. Representation can be achieved in many ways, such as
evoking sensory experiences through descriptive language, voicing characters through
dialogue and setting the mood through emotional descriptions of the setting. Rather than
understanding representation as encoding some objective meaning, this framework takes a
reader-response stance, viewing representation as offering provocations and opportunities
to the reader. In Rosenblatt's (1968) account of reading as a unique, historically grounded
transaction between a reader and a text, each is transformed. The reader's identity is
changed through her response to the text, which then reciprocally transforms the text's
possible meanings (Barthes, 1981).
One way we can interact with computation is through modeling or simulation.
Interacting with computational models is a central practice in science (NGSS Lead States,
2013; Blikstein, 2014) and computer science (K-12 Computer Science Framework, 2016).
Interacting with a model can be agent-based, emphasizing how one actor in the system can
affect others, or systemic, emphasizing emergent properties (Weintrop et al., 2016). Papert
(1980) used the term microworlds to describe computational models or simulations in which
one can immerse oneself and learn how the world works through play or exploration. This
can lead to authentic, embodied knowledge, more like getting to know someone than
learning a fact. For example, NetLogo (Wilensky, 1999) is an environment for modeling of
dynamic systems. Participating in a NetLogo simulation can help students understand and
predict the behavior of systems from both an agent-based and a system-level perspective
(Wilensky and Stroup, 1999). This article considers microworlds to be both models and
games[1].
Interactive storytelling combines the affordances of text and code in ways that are
difﬁcult to classify, so the modes of interaction described in the previous two paragraphs are
best understood as heuristics for the affordances authors might perceive in interactive
storytelling, as instantiated in the Web application's interface. Much of the participatory
design process developing the Web application was devoted to discovering the ways
authors could use interactive storytelling and reﬁning the interface and pedagogy to make
those affordances more perceptible.
Rhetoric. The second layer, rhetoric, is focused on how authors use the affordances of
media to create meaning. Theorists of digital rhetoric have argued for the importance of this
link: whereas traditional literary criticism could assume some universality to how text
functions, digital media cannot be understood apart from the affordances of its media
(Wysocki, 2004; Bogost, 2007; Brooke, 2009). Digital interfaces such as hypertext, interactive
stories, Instagram and mobile phones have such diverse affordances that the rhetorical
possibilities of each are quite distinct.
The interactive storytelling community has identiﬁed several broad categories of
rhetorical moves (Glassner, 2004; Montfort, 2007; Murray, 2017). Ryan (2001) contrasts
immersion with interactivity. Reading a story can involve constructing a world of meanings
around oneself through a transactional reading process. The reader potentially experiences
immersion, a sense of being embodied in and surrounded by that world. In contrast, when
playing an interactive story which functions as a microworld, it does the work of simulation
and its world is perceived as outside of oneself. The player experiences interactivity, with a
heightened awareness of the interface. There may be a tradeoff between these rhetorical
modes in interactive storytelling: the more the story handles the simulation (functioning as a
microworld), the more one can interact with dynamics that are too hard to simulate or which
one could not have imagined. The more the reader is left to do the simulation (as with a
representational text), the more she can experience intimacy and empathy through
immersive embodiment.
This article's analysis of the rhetoric of interactive storytelling extends traditional
reader-response literary analysis to include what Bogost (2006a, 2006b) calls procedural
rhetoric, or the ways computational affordances are used to inﬂuence an imagined player.
The focus is on how stories are crafted to make available possible readings. When available,
participants' reﬂections on their intentions are used to support this analysis. Common
interactive techniques include providing or denying agency to the player, allowing
omnipotent control of the world (for example, allowing the player to choose the reactions of
others or whether it rains) and inserting parenthetical remarks on the player's choices.
Immersive techniques include allowing the player to construct an in-world identity and
structuring choices so that the player becomes morally implicated in the story's events or is
presumed to have given consent to events taking place in the story.
Figured meanings. The third layer, ﬁgured meanings, describes the potential effects of
rhetorical techniques used by interactive stories. These may include how others read the
story and respond by reshaping their own identities, as well as by reshaping the sensemaking processes available for reading other texts. Following the earlier deﬁnition of
identity as the interface between internal self-conception and externally imposed
subjectivities, changes to ﬁgured meanings may expand or contract the kinds of identities

possible within the literacy space. As a concrete example, when a literature class reads texts
featuring characters with potentially invisible life experiences such as being immigrants,
queer or homeless, these possible selves become more available to students' identities.
In the participatory design process, one common way interactive stories reshaped sensemaking processes was by invoking existing genres or developing new genres. Genres
include literary genres such as horror, science ﬁction and role-playing games, as well as
what Bakhtin and Holquist (1981) call speech genres, or the “sphere[s] in which language is
used [and] develops its own relatively stable types” (p. 60). In their stories, participants used
speech genres including quizzes, text messaging conversations and Facebook posts. Story
topics, such as family, friends, dating and school, function similarly to speech genres in that
they create expectations for the kinds of meanings that will be expressed. To be recognized,
an author or speaker must adopt a register, a socially recognized form of communication
which indexes some qualities of the speaker (Agha, 2005). By introducing speech genres in
their stories, participants pushed for social recognition of new registers within the literacy
space.
Critical possibilities. Finally, the fourth layer, critical possibilities, are ways in which
stories enact or hold open the possibility of critical change. This article refers to critical
literacy practices as those with the potential to enact transformation both within the literacy
space (by changing the actors or the sense-making processes) and also beyond the literacy
space (Gee, 2004a, 2004b). Fairclough (2004) refers to the performativity of texts as their
“causal effects on nonsemiotic elements of the material, social, and mental worlds and the
conditions of possibility for the performativity of texts” (p. 225).
When people ﬁnd themselves within oppressive literacy spaces, where the existing
language and cultural materials offer only marginalized subject positions, there are several
possible responses. One might refuse to participate, retreating into the space of inner speech
where for Bakhtin (if not for Vygotsky), one is free to fashion a self. One might also try to
“use the master's tools to dismantle the master's house” (Lorde, 2003), or insist on the
inclusion of other materials, for example, by legitimizing vernacular registers (Anzaldúa,
1987). Discovering and using critical strategies depends on understanding how identities are
circumscribed by available subjectivities, and how registers are legitimized.
The goal of Freirian critical literacy is to develop this understanding. Freirian critical
literacy depends on the representational function of text: once people become aware of the
parallels between reading the word and reading the world, they may realize that neither has
a ﬁxed meaning, but rather the meanings of each are continually produced within a literacy
space, and that the possible meanings are co-produced with one's identity. Of course, as
mentioned earlier, it is much easier to open new possibilities for identity and register within
a small discussion group than it is within the context of ideologies that span centuries and
continents.
The computational affordances of interactive stories support additional critical
possibilities (Bogost, 2007; Blikstein, 2008; Garcia et al., 2015). One powerful dynamic which
emerged in the participatory design workshops was using interactive stories to model
literacy spaces themselves. For example, participants wrote stories allowing the player to
experience how one is treated differently when speaking English versus when speaking
Spanish, or how two friends in casual conversation can also be engaged in a struggle to
position each other. These stories foreground otherwise-latent uses of power within the
literacy space, making them visible and accessible for analysis and critique. These stories
potentially function as critical discourse models, a particular kind of what Vossoughi (2014)
refers to as social analytic artifacts, or “tools that deepen the collective analysis of social
problems” (p. 353).

Players of critical discourse models participate in the story's simulated literacy space. At
the same time, the player and the story are both actors within a larger literacy space. The
idea of a nested literacy space as an actor within a larger literacy space is not new: Bakhtin's
(1981) multivocal understanding of texts in dialogue with existing meanings and Minsky's
(1988) understanding of minds composed of many agents may each be understood as
literacy spaces functioning as actors within larger literacy spaces. However, the distinct
affordances of interactive stories (particularly the precision with which one can author them)
offer unique critical possibilities.
Interactive storytelling
The goals of this research are to develop media and pedagogy capable of supporting textualcomputational multiliteracy, to study the practices that might emerge and to assess their
critical possibilities. The starting point is interactive storytelling (a generalization of
interactive ﬁction), a medium authored with text and code to create single-player text-based
games and stories. Interactive storytelling had a widespread following from the late 1980s
through the 1990s, bounded chronologically by the emergence of personal computers and
early access to the internet and its displacement by graphical games made possible by
improvements in processors and displays (Labrande, 2011). Over the past several decades,
interactive storytelling has retained a small but active community, often articulating
feminist and queer critical responses to the ideologies dominant in the literacy space of
mainstream video games (Anthropy, 2012).
Two recent works of interactive storytelling illustrate the dynamics the framework
presented in the previous section: these stories use their affordances for immersive and
interactive rhetorical effect, producing ﬁgured meanings and critical possibilities. In 80
Days (2014), a choose-your-own-adventure game loosely based on Jules Verne's novel, the
player inhabits the role of Passepartout, valet to a wealthy Englishman who is attempting to
circumnavigate a counterfactual nineteenth-century world. In choosing how the story
should unfold, the player may have very different experiences depending on how she
engages dialogically with other characters, and the ways in which she decides to explore
beyond the bubble formed by her employer’s casually racist, sexist and elitist attitudes. In
the interplay between interactivity (making strategic choices) and immersion (becoming
invested in the lives of other characters), 80 Days functions as a microworld in which the
player can discover how richly expansive or foreclosed the world (and one’s self-authored
identity) can be, depending on the extent to which one chooses vulnerability and openness in
the face of the unknown. The player potentially realizes that winning the game is not the
point.
Nicky Case’s Coming Out Simulator (2014), an autobiographical “half-true story about
half-truths,” powerfully demonstrates the capability of interactive storytelling to model how
linguistic processes produce our social reality and shape how we can act within them. The
game replays the evening during Case’s teenage years when he told his parents (or, perhaps,
they found out) that he is bisexual. The interface mimics that of a mobile phone,
superimposing text message speech bubbles over simple animations and presenting the
player with dialogue options. In the prologue, the game highlights the way it functions as a
critical discourse model, emphasizing that all the characters remember and respond to
everything the player does. As the protagonist struggles to come out to his parents, they are
equally committed to preserving their image of him by silencing his attempt at selfredeﬁnition. The story is ultimately about negotiating what it means to be male and to be a
good son within a cultural context. It is played through speech acts; the player struggles to

author an identity using language whose categories and meanings are largely under the
parents' control.
We engage in these discursive struggles on a daily basis, but because they are ﬂeeting
and invisible, they can be difﬁcult to perceive or understand. In contrast to our lived
experience or linear narrative, in which we can only follow one path through a space of
possibilities, the Coming Out Simulator:

[. . .] includes dialogue that I, my parents, and my ex-boyfriend actually said. As well as all the
things we could have, should have, and never would have said. It doesn’t matter which is which.

The game takes no more than 20 min to play through, and it explicitly invites multiple
replays through which a player can map out the space of interactional possibilities. In doing
so, the player engages in an epistemic game (Collins and Ferguson, 1993) of modeling how
characters position themselves and each other and analyzing the how the game’s reality is
shaped by the characters’ speech choices. Both 80 Days and the Coming Out Simulator
illustrate the critical potential of interactive storytelling as a medium for textualcomputational multiliteracy. Studying language, identity and culture within a
computational environment could make it possible to simulate, replay and share these
otherwise-elusive phenomena. Reading and writing microworlds in the context of questions
usually addressed by literature might imbue computer science, a potentially abstract and
impersonal ﬁeld, with profound personal signiﬁcance.
Workshops I and II: developing Unfold Studio
This section reports on the initial development of Unfold Studio through Workshops I and II
with middle-school students. An iterative design process focused on emergent and imagined
interactive storytelling practices helped develop the Web application and the analytical
framework described above. These results framed a hypothesis that interactive storytelling
could be particularly effective in supporting critical change within and beyond the
classroom literacy space. Workshop III designed to test this hypothesis is reported in the
following section.
Methods
The workshops developing Unfold Studio took place at a private all-girls' middle school in
western USA, at the border of two communities: a wealthy, largely white and East Asian
community, and a largely black, Latinx and Tongan community, including many recent
immigrants and having a much lower socioeconomic status. Approximately 80 per cent of
the students pay full tuition; the majority of students receiving scholarships are MexicanAmerican and speak Spanish at home. In spite of the structural inequalities that come with
charging high tuition, the school's explicit mission is to help its early-adolescent students
understand gender, sexuality and race. Students had these analytical registers available to
them, but there were also numerous tensions dividing the school that were seldom openly
discussed. The ﬁrst author who led these workshops (hereafter “Chris”) had been a teacher
at the school several years prior, granting him legitimacy and trust in the eyes of the faculty.
Even though he had never worked with these students before, they also accorded him
insider status.
Workshop I included 12 participants who met for 3 h each morning over the course of a
school week (15 h in all). The participants were consistently positioned as co-researchers. On
the ﬁrst day, Chris introduced interactive storytelling and an initial prototype of the Web
application, saying he did not know what it might be good for. He proposed a writer's
workshop-like structure, with mini-lessons targeting writing skills such as incorporating
dialogue, developing character, using sensory detail and structuring plot, as well as
computational skills such as expressing stories as sequences and branches, using loops and
conditionals and using trees and directed graphs to plan their stories. As the week went on,
participants increasingly steered the agenda. The ﬁnal 30 min of each day were devoted to
discussing what worked and what did not work in the lessons, planning the following days
and critiquing the Web application. Each night the authors updated the Web application
guided by the participants' feedback. The authors collected ethnographic ﬁeld notes, logged
interactions with the Web application, analyzed the stories participants wrote and asked the
participants to engage in reﬂective writing at the end of each session.
Workshop II was embedded within a two-week summer program designed to build
community amongst students receiving full scholarships to the same school. The
participants were 16 incoming sixth-grade students (age, 11-12 years), all bilingual speakers
of Spanish and English. Chris also had the opportunity to plan and co-teach the workshop
with an incoming eighth-grade student, a college sophomore majoring in creative writing
(both alumnae of the same program), and the students’ future humanities teacher. This
group designed a sequence of three introductory story prompts, and otherwise prioritized
time for writing and workshopping stories with optional mini-lessons.
The college student in particular engaged the participants with a powerful writerly
presence. In speech and writing, she allowed herself to be vulnerable and direct in her
perceptions, unafraid to follow thoughts even when they approached topics that felt taboo.
One participant noted:
I was struck by the diﬀerence between her real story and my skeleton of a story. Juli’s (all
participant names are pseudonyms) had an authenticity, a sensory immediacy that was so vivid it
was almost uncomfortable.

The authors repeatedly noted participants authoring their identities by writing about real
issues (and sharing their stories) after Juli opened space to do so.
Development of the application was guided by participants' emergent and imagined
interactive storytelling practices. To understand these, the authors analyzed ﬁeld notes and
participants' written reﬂections using a grounded theory afﬁnity analysis (Iba et al., 2017) in
which data were clustered and interpreted. The resulting patterns described how
participants recognized affordances in the medium, how they used the medium rhetorically
toward ﬁgured meanings and how they used the medium for critical analysis.
Results
Developing aﬀordances. The initial prototype allowed users to browse the library of
published stories and to select an individual story to play or edit. When viewing an
individual story, two panes were presented for editing and playing, in much the same
manner as Scratch (Resnick et al., 2009). Stories are written in Ink, a language originally
designed to support the development of 80 Days and released as open source in 2016.
Figure 1 shows a story written in Ink, demonstrating several of its key structures. The
narrative is divided into knots containing anywhere from a phrase to several paragraphs of
prose. Typically, a knot ends with several options to be presented to the player, whose
consequences are redirects to other knots.
In response to participant feedback, three iterations were released over the course of the
week. The participants delighted in suggesting improvements and reporting bugs and
checking that the changes had been made. The most frequently requested features were
support for additional typefaces, font styles, font sizes and colors. Participants also
requested support for visual elements such as background colors and incorporating

Figure 1.
Final interface for
Unfold Studio

animated GIFs into their stories, user accounts with the ability to mark stories as private
and site navigation elements such as the ability to search, star favorite stories and add short
descriptions to stories for ease of browsing. Participants came across several situations in
which they needed to toggle between a prose-like interface and a code-like interface. Several
participants attempted to use accented Spanish characters and emoji in their stories. At the
time, Ink did not support unicode, so these characters caused the application to crash.
In both Workshops I and II, participants' use of computational affordances was broad
but shallow. In Workshop II, 81 per cent of stories used branching to create nonlinear
structure, but less than 20 per cent used other computational affordances such as variables,
logic, or randomness, despite mini-lessons focused on exploring their use. One frequently
cited constraint was that error messages were not user-friendly. Nevertheless, many
participants described the computational concepts as interesting and generative.
Aﬀordances spurred imagination for rhetoric and ﬁgured meanings. Over the course of
Workshop I, participants explored the nature of interactive storytelling, positioning it with
respect to stories, games and computer programs, and playing and critiquing several
published examples. These conversations generated a great deal of aspirational discussion
about what could be created with interactive storytelling. When participants imagined
“being lost” in a story world, “going deeper into characters” and “a world of different types
of people,” the experiences they described were immersive readings. These generally relied
on familiar representational affordances of literary text (also called literary elements) such
as sensory detail, characterization and point of view.
Participants also imagined using interactivity, though not for new forms of digital media
such as games, agents or simulations of systems. Instead, participants often described a
desire to concretize an imagined reader's experience, to connect with the reader and to shape
her reading of the story. One participant wrote, “I love it because [. . .] I feel like a writer [. . .]
you give the viewers the opportunity to make the story their story by choosing what path
they want to take.” This participant imagined using interactive storytelling in much the
same way as Graff et al.'s “They say, I say” (2006) pedagogical strategy for helping
participants understand voice in academic writing, using choices and nonlinear branching
to represent possible readings. Helping students learn that reading is an active, interpretive
process (Rosenblatt, 1968) rather than one of passive uptake is a central goal of English/
Language Arts and Freirian critical pedagogy, made particularly challenging because the
student usually cannot observe the practices adopted by the expert reader.
Participants imagined writing various simulations of dialogical encounters, particularly
in digital media. They frequently requested the ability to add emoji, GIFs and speech
bubbles simulating text message conversations. Participants' desires to appropriate these
speech genres into their own storytelling (e.g. embedding texts or tweets into an interactive
story) are evocative of Bakhtin's (1981) analysis of how the novel ﬁxes and stylizes other
genres, while making them more “free and ﬂexible [. . .] permeated with laughter, irony,
humor, elements of self-parody” (p. 7) by putting them in dialogue with other voices. Social
media is already dialogic and constantly changing, but platforms allow only prescribed
usage aimed at commodifying the voices, identities and attention of users. The unauthorized
uses imagined by these workshop participants point to new strategies for critical
engagement with computational media.
Critical discourse models. One prominent theme which emerged in Workshop II was talk
about language. One of the initial story prompts asked participants to model a real-life
incident where each participant had a different experience. Many participants drew on their
bilingualism to model how social reality changes when speaking English and when
speaking Spanish. For example, one story considered a multilingual family context in which
the player can position herself by drawing on a spectrum of linguistic practices. Others
explored discrimination which results from speaking Spanish in public, or represented a
multilingual inner voice. These stories functioned as dialogue-based microworlds
simulating both heteroglossic possibility and exclusionary language ideologies (Rosa and
Burdick, 2016).
The classroom sustained a lively and thoughtful conversation exploring these questions.
Field notes and participants' post-workshop reﬂections document the importance to
participants of constructing, revising, playing and discussing these interactive stories. The
authors' ﬁeld notes repeatedly describe participants juxtaposing their desks so that each
could face her laptop screen and her partner while reading and writing – an embodied
enactment of the literacy space. The stories functioned as what Vossoughi (2014) calls social
analytic artifacts, “tools that deepen the collective analysis of social problems” (p. 353).
However, the speciﬁc method by which the stories functioned, as microworlds simulating
discourse within a literacy space, led to a new concept: critical discourse models. Critical
discourse models may offer experiences which cannot be enacted with immersive
representational texts, and introducing them as actors within a literacy space may offer new
possibilities for critical literacies pedagogy.
Workshop III: toward critical multiliteracies
The result of Workshops I and II was a medium capable of supporting textualcomputational literacy practices through interactive storytelling, and a hypothesis that
these practices could be particularly effective in supporting critical change within and
beyond the classroom literacy space. Following Schwartz et al.’s (2008) suggestion that
design-based research ought to move from innovative design toward efﬁciency, we designed
Workshop III to test this hypothesis.

Methods
Workshop III was set in a large comprehensive high-school drawing students from the same
communities as the previous studies. The workshop took place over two weeks (15 h total) in
students' English and Sociology classes, linked together in a self-selected academic track
focused on social justice. Twenty-three high-school seniors participated; two additional
students did not return consent forms and were excluded from analysis. The ﬁrst author codesigned the workshop with several of the students during meetings and email exchanges
prior to the workshop, and co-led the workshop with two of the students' teachers. His
collegiality with the other teachers conferred legitimacy and some authority, while his
intentional self-positioning as a researcher beyond the school's authority may have
contributed to participants' willingness to discuss and write about charged topics.
The workshop was again structured as three introductory story prompts introducing
affordances of interactive storytelling, followed by writer's workshop time devoted to
participants working on, sharing and revising their interactive stories. The ﬁnal prompt
addressed three ideas related critical understandings of discourse:
 Models of personhood: In any social world, people inhabit models of personhood
which deﬁne what kind of person they will be seen as and what they can do.
 Performativity: Identities are dynamic, not static. We perform our identities,
bounded by models of personhood, but possibly also redeﬁning models of
personhood.
 Register: A socially recognized way of speaking based in a model of personhood.
Participants were offered several options for exploring the following ideas:
 create an oppressive social world where the possibilities of speech are limited for the
main character;
 create a world where the main character is assigned a model of personhood based on
how he/she speaks; or
 create a world where the main character subverts a model of personhood he/she is
assigned.
As they discussed these prompts, many participants offered examples from their own lives.
Many participants continued to develop stories based on these prompts for the rest of the
workshop.
Participants' stories were analyzed through multiple iterations of qualitative coding.
Initially, the authors relied on open coding via a grounded theory approach (Charmaz, 1996).
Over multiple passes of coding, writing integrative memos (Emerson, Fretz, and Shaw, 2011)
and reﬁning the coding scheme, the outlines of the analytical framework (presented above)
emerged. Two major groups of computational affordances were FLOW, affordances for
controlling the ﬂow of story execution, and STATE, affordances for keeping track of the
past and using it to affect the future. Of the various textual affordances, DIALOGUE was
chosen for further analysis because of its importance for critical analysis of social discourse.
Codes for rhetorical strategies were grouped into IMMERSION and INTERACTIVITY.
Figured meanings were grouped into three high-level categories: LIFE, for speech genres
pertaining to family, dating, friends, jobs, school and drug use; LITERARY GENRE,
prominently including science ﬁction, horror and genres of games such as role-playing
games and puzzles; and SOCIAL MEDIA, for stories adopting registers characteristic of
texting or other online discourse. Finally, CRITICALITY contains codes for when categories
such as race, gender, sexuality and social class are either marked (for example, by noting a
character’s skin color or manner of speech) or explicitly addressed by the story. Cooccurrence of codes within stories was calculated to analyze associations between
factors at different layers of the analytical framework. The ﬁnal codebook is included in
Appendix 1[2].
Results
The results, shown in Table I, validate the construct of critical discourse models as an
effective structure for exploring critical ideas in real-life contexts. Of the stories with critical
engagement (CRITICAL), 62 per cent dealt with familiar settings such as family, friends,
dating and school (LIFE), 62 per cent used immersive techniques (IMMERSION), 85 per cent
used interactive techniques (INTERACTIVITY), 69 per cent used computational
affordances to control story ﬂow (FLOW) and 92 per cent relied on dialogue (DIALOGUE).
These are precisely the properties hypothesized to be effective for exploring critical ideas.
There was a clear distinction between the use of computational affordances for
controlling the ﬂow of story execution (FLOW) and the use of variables to maintain state
(STATE). FLOW affordances tended to occur in stories using both immersive (47 per cent)
and interactive (71 per cent) techniques, while STATE affordances were seldom used in
immersive stories (17 per cent) and more often used in interactive stories (42 per cent). While
FLOW stories engaged with LIFE (41 per cent) and LITERARY GENRE (47 per cent)
ﬁgured meanings, STATE stories focused predominantly on LITERARY GENRE. (The sets
of stories coded with LIFE and LITERARY GENRE were disjoint.) Finally, 53 per cent of
FLOW stories featured critical engagement (CRITICAL), compared with only 31 per cent of
STATE stories. Broadly, these results suggest that FLOW affordances were often important
components of critical discourse models, while STATE affordances were more often games
or puzzles set in ﬁctional worlds, whose ﬁgured meanings had lower stakes.
One particularly interesting set of stories were set in the speech genres of text messaging
and social media. These stories effectively made use of affordances and rhetorical strategies
such as acronyms, iconic textual effects, emoji and pacing – either the staccato of brief
exchanges or ellipses denoting signiﬁcant pauses. The affordances shared by texting, social
media and the interactive storytelling medium have become infrastructural (diSessa, 2000)
to identity in many youth cultures. Holland et al. (2001) emphasize that identities are
authored within literacy spaces dependent on material conditions; as these conditions
change, identities must be articulated anew. The prevalence of social media as a space of
youth identity practices may make interactive storytelling particularly valuable for
authoring identities and critical analysis of the literacy spaces in which they are authored.
Case study: enacting critical change
A case study of one participant's experience in the workshop shows the potential critical
discourse models have to enact change in and beyond the literacy space. In an introductory
survey, Leanne describes herself as female, biracial and primarily a speaker of standard
English with African-American vernacular English at some family gatherings. Her presurvey responses suggest a rich history of textual literacy practices, and very little history
with computation. Leanne experiences gender-based discrimination frequently and racial
discrimination daily. Leanne was an active, but not extremely vocal, participant in the
workshop. Some days she sat by herself and worked, other days she sat with a small group
of peers. She participated regularly in the quiet conversation taking place while participants
read and wrote. In a survey halfway through the workshop, Leanne described having
trouble deciding what to write about:

Flow (17)
State (12)
Dialogue (22)
Immersion (15)
Interactivity (21)
Life (13)
Literary Genre (15)
Social media (9)
Critical (13)

Code (count)

100
42
50
53
57
54
53
22
69

Flow (%)
29
100
32
13
24
23
53
33
31

State (%)

Affordances

65
58
100
87
71
77
47
67
92

Dialogue (%)
47
17
59
100
52
85
13
56
62

Immersion (%)
71
42
68
73
100
77
60
33
85

Interactivity (%)

Rhetoric

41
25
45
73
48
100
0
67
62

47
67
32
13
43
0
100
0
23

12
25
27
33
14
46
0
100
23

Figured meanings
Literary
Social
Life (%)
genre (%)
media (%)

53
33
55
53
52
62
20
33
100

Critical (%)

Criticality

Critical
literacies of
text and code

299

Table I.
Relative cooccurrence of codes
(columns) in stories
with codes (rows)

I grasp that I can pull from my own experiences, but I have trouble picking just one. I know that
when I do, it could end up being pretty profound, but I haven't been able to zero in on one concept
yet.

In the ﬁrst week, she wrote a fan ﬁction-style story set in the world of Dune, which her
English class had been reading. She also reported having some trouble with the
programming aspects of interactive ﬁction: “I think I get the gist of it, but an error occurred
on the story I did write. I don't know how I can ﬁx these errors; the explanation given when I
click on my story is still confusing to me."
At the beginning of the second week, an incident took place which motivated Leanne to
write her ﬁnal story. During a discussion on register, Mr Leo, a white man who was one of
the co-teachers, shared an anecdote in which he had imitated the speaking style of several
African-American freshmen girls he did not know well. He described how he had intended
the interaction as a joke and a way to connect, but they were extremely offended. He
explained that they would not have taken offense if they had been in his class, because they
would have known him as someone who likes to tell jokes and understood his intentions. No
participant responded to this anecdote at the time, but Leanne addressed it in her ﬁnal
reﬂection:
I was intrigued by the discussion on personhood and register, and the idea of having no way out
of the stereotypes you are assigned. Mr Leo gave an example of register discussing some
insensitive things he said to a couple of African-American freshmen girls, saying the same oﬀense
wouldn't happen in this class. I disagreed, since I was very oﬀended by his words and conclusion,
but didn't say anything in order to not make people (especially Mr. Proctor who I didn't know
very well) “uncomfortable.” I regretted not saying anything, and I think that regret evolved into
my piece.

An excerpt from the story Leanne wrote in response to this incident is included below.
Readers may play it as an interactive story by visiting https://unfold.studio/stories/1063.
The story uses only FLOW computational affordances, offering nonlinear paths through
knots (e.g. === start ===) of content. Knots end by presenting the player with options (*)
which divert the story to another knot (!). When readers play the story, they see only the
text contained within knots and their options. Readers may also choose to view the story's
source code in parallel (see Figure 1).
Leanne's story functioned as a critical discourse model. It enacted critical transformation
within the classroom literacy space by indirectly voicing an otherwise-unspoken
contestation of Mr Leo's anecdote. The story is written in second-person, which highlights
the player's role as a character in the story. The story begins by introducing Angela, a girl in
your (presumably high school) class who has “dark skin, curly hair, and lively eyes, and
she's probably the smartest kid in your grade” (Line 3). The ﬁrst choice the player is
presented with is not an action in the story but a choice of identity: deciding whether to like
Angela or whether to be jealous of her. This is the beginning of a process by which the
player self-authors an identity within the story, and thereby makes herself a witness and
complicit in the action. Regardless of the player's choice, the plot continues with another girl,
making a joke about how Angela is so poor that she probably has to wear second-hand
clothing to school. The player is offered at least one opportunity to defend Angela against
the attacks (Lines 37, 60, 70). However, the player's protests are ultimately ineffectual.
Standing up for Angela only gets the player ostracized too (Line 75).
Angela: A Bystander’s Story (Lines 50-73)
50 === yet ===
The rumor gets back to Angela within the week. You keep an eye on
her, wonderingif she is affected, but she seems to be handling
all of this with grace. Angelacontinues to be a strong student,
and is kind to the people around her. Thegirl who began the rumor becomes aggravated. One day you hear her shout at
Angela, “You ﬁlthy n*gger!” Angela stares at her, stunned, her
unaffected smilecompletely gone. She looks wounded. You know
that a horrible line has been crossed.
*You are shocked into silence.
-> bullyA
*You tell the girl, “That's too far. Stop it.”
-> bullyMe
=== bullyA ===
The new game spreads like wildﬁre. Angela is shoved on the
staircase, excluded
from everything. The word “N*gger” echoes through the halls
and is written inSharpie on her backpack. It scares you how
awful your classmates are being toAngela. You never thought
she was a bad person; what has she done to deservethis? More and
more, Angela reacts to the taunts with a rag doll's indifference. Her empty eyes haunt you. At ﬁrst she looked wounded, but
now she looks dead.
*You've had enough. You tell your friends to stop.
-> bully
Me*If you say anything, you know they'll come after you too, so
you say nothing.
-> fear

Regardless of the player's earlier choices, she ends up in the pivotal sequence at Line 50,
excerpted above. Angela's refusal to be provoked by the mean joke causes the girl to escalate
her attacks, which ﬁnally overwhelm Angela's composure. The player is faced with two
options recapitulating the earlier structure, to either remain in shocked silence or to defend
Angela. If the player does nothing, the attacks escalate (Line 63). Angela still does not respond
to the attacks, but now instead of “handling all of this with grace” (Line 52), she reacts “with a
rag doll's indifference” (Line 68). The player is offered one ﬁnal chance to stand up for Angela
as she goes from looking “wounded” to “dead” (Line 69). If the player stands up for Angela at
either opportunity, she reaches one of two possible story endings. For the ﬁrst time, the player
is positioned racially – as a “White N*gger” (Line 77). The story concludes with the player's
removal from school. Alternatively, if the player chooses not to defend Angela, the player's life
goes on – the player dissociates from Angela and disappears from the narrative altogether. It
becomes clear that the racial attacks were always about power: “The girl who started it all is on
top of the world, the queen bee; the school is hers now. Angela is so far below her in the social
hierarchy that she never has to feel jealous again” (line 88). In both outcomes, the player
watches as Angela is dehumanized: she no longer makes eye contact with the player, is
described as “IT” (Line 76) and is described as the other students' “plaything” (Line 93). In both
endings, the narrator relates that Angela attempts suicide.
In neither outcome is the player able to meaningfully protect Angela; the only choice is
whether to be stripped of one's whiteness and subject oneself to the same attacks, or to remain
silent. The story offers no way out, nor does it make available exculpation or solidarity. Both
immersion and interactivity are at work: the high stakes and appearance of choice invite replay
and exploration of the action space in an attempt to ﬁnd a solution. The parts of the story where
the player's action is narrated rather than selected, and particularly the vivid imagery showing

Angela's facade cracking, eyes dimming and progressive dehumanization, implicate the player
in the story. A player might feel both inside and outside the story, and the effect could be a
transformation of the player's identity within the world of the story as well as in the real world.
In refusing to grant the player agency, the story possibly enacts critical change in its literacy
space, for example, by arguing against the easy answers of an anti-bullying curriculum
claiming that bullying can be stopped by a simple act of moral courage.
The story functioned as a critical discourse model within the workshop. As Leanne wrote
in her closing reﬂection, writing it was an opportunity to think about the dynamics by which
someone can be trapped and silenced in models of personhood and a way for her to speak
back against her teacher's assumptions. While this did not lead to a confrontation with Mr
Leo or a reckoning with his joke, Leanne's story did contribute to change. In the ﬁnal days of
the workshop, the authors noted participants increasingly frequently sitting in pairs or
triads, reading and discussing stories. One question on the closing survey asked
participants to write an open-ended reﬂection on new ideas they considered in the workshop.
In total, 44 per cent of respondents discussed ideas related to criticality or empathy, often
using forceful language to describe their interaction with the stories. For example, one
participant wrote, “I enjoyed learning about how interactive ﬁction can drive people to
explore/understand limits and effectively force people to empathize."
Discussion
The design-based research reported in this article yielded fruitful answers to the initial
research questions. The ﬁrst two studies explored the potential uses of interactive
storytelling and developed the Web application's affordances to better support participants'
aspirations for the medium. Workshop III validated critical discourse models as tools for
critical engagement and documented the role of textual and computational affordances. In
each workshop, the participants were involved in planning the workshop, framing the
questions and interpreting the results. Their participation was essential to the validity of
the ﬁndings and also to ensuring that the research process could play an equitable role in the
literacy spaces which were the focus of study.
This research makes three primary contributions. First, the iterative participatory design
process yielded a reﬁned Web application capable of supporting textual-computational
multiliteracy in a writer's workshop environment. Development followed (and continues to
follow) workshop participants' imagined uses for interactive storytelling, so that the workshops
themselves were a critical process of enacting imagined conditions. Unfold Studio has been
publicly released and has already been used in several schools, including several months in an
introductory computer science course, as well as in a teacher preparation program and
professional development workshops focused on computer science and critical literacies.
Framing interactive storytelling as an introductory approach to programming may help
teachers of computer science view their subject as a literacy, as a resource for their students'
existing multi- and transliteracy practices, and as an opportunity to support their students'
critical perspectives. The expansion of Unfold Studio as an online literacy space and its efﬁcacy
as an introduction to programming are topics of ongoing research (Proctor, 2019).
Second, this research ﬁnds theoretical common ground between learning scientists and
scholars of critical literacy, and it demonstrates the importance of continued dialogue between
these communities. There is substantial overlap between the constructs used by each ﬁeld to
study situated, distributed and mediated meaning-making; this article's framing of literacy
spaces may be useful for integrating the perspectives and concerns of each ﬁeld. This work is
particularly urgent given the current emphasis on increasing access to K-12 computer science.
Over the past two decades, the computer science education community has devoted increasing

attention to educational equity (Margolis and Fisher, 2003; Margolis et al., 2010; Kafai and
Burke, 2013), focusing on unequal participation in computing and factors causing it. This work
is important but incomplete. Too often, efforts toward more equitable participation do no
critical interrogation of the practices in which they seek to increase participation. There are
direct parallels to the decades of work by scholars and practitioners of English/Language Arts
grappling with how and when to teach dominant American English. Computing too has a
culture of power (Delpit, 1988) and a tendency to view other sense-making practices through a
deﬁcit lens (Moll et al., 1992). What might computer science look like if it centered culturally
sustaining pedagogy (Paris, 2012), with its insistence on criticality?
Finally, this research yields the concept of critical discourse models, which may be
particularly effective in supporting critical awareness in the multi- and transliteracies
prevalent in youth culture today. Interactive storytelling offers affordances useful for
modeling and analyzing in-person and digitally mediated discourse. Because they make
phenomena visible and concrete, critical discourse models may be especially useful in
contexts where people have different amounts of experience thinking about these concepts.
For example, Unfold Studio was used in a course on literacies in a teacher preparation
program where some participants had chosen to become teachers to combat the oppression
they experienced on a daily basis. For others who had grown up in privilege, goals of social
justice were not grounded in lived experience. These are often particularly difﬁcult settings
in which to discuss power and privilege. Those coming from habitual and seldomquestioned privilege may feel they need a nonjudgmental space to consider new selfunderstandings, and feel threatened by critical positions. However, for people who
experience marginalization on a daily basis, the insistence on a safe space which excludes
uncomfortable truths can be experienced as an act of erasure by dominant literacy practices.
In such a space, interactive storytelling can be used to model experiences such as
microaggressions. Those who do not understand how an offhand comment can shatter one's
sense of safety and belonging can play and replay an interactive story, empathizing but also
coming to understand the mechanisms by which microaggressions can cause harm.
Conclusion
As our society completes its shift from print text to digital media, schools must prepare
youth to participate in new forms of literacy. It is clear that computational media do not
necessarily lead to the just, peaceful and inclusive social structures imagined by the pioneers
of personal and social computing. Indeed, computational media have enabled powerful new
forms of surveillance, control and ampliﬁcation of oppressive ideologies. If we want to
support youth in self-authorship, critical agency and participation in designing sociotechnical futures, it is imperative that our schools cultivate critical computational literacies
which center the lives and identities of the community. The design-based research reported
in this article yielded a concrete step toward that goal. As Unfold Studio makes its way into
classrooms and writing clubs, future research will continue the project of developing a
medium well-suited to supporting critical literacy practices.
Notes
1. There is much more to say about the nature of games, which is not taken up in this article. In the
early 2000s, there was a ﬁerce debate between narratologists and ludologists about whether
games ought to be analyzed using the machinery of literary criticism. The competing framings of
games ran roughly parallel to the representational texts and microworlds presented here.
2. Appendix 1 is available online at http://chrisproctor.net/research/unfoldstudio

References
Aarseth, E. (1997), Cybertext: Perspectives on Ergodic Literature, Johns Hopkins University Press,
Baltimore, CA.
Agha, A. (2005), “Voice, footing, enregisterment”, Journal of Linguistic Anthropology, Vol. 15 No. 1,
pp. 38-59.
Anderson, T. and Shattuck, J. (2012), “Design-based research: a decade of progress in education
research?”, Educational Researcher, Vol. 41 No. 1, pp. 16-25.
Anthropy, A. (2012), Rise of the Videogame Zinesters, Seven Stories Press, New York, NY.
Anzaldúa, G. (1987), Borderlands: La Frontera: The New Mestiza, Aunt Lute Books, San Francisco, CA.
Bakhtin, M. and Holquist, M. (1981), The Dialogic Imagination: Four Essays, University of TX Press,
Austin, TX.
Bang, M. and Vossoughi, S. (2016), “Participatory design research and educational justice: studying learning
and relations within social change making”, Cognition and Instruction, Vol. 34 No. 3, pp. 173-193.
Barab, S., Thomas, M., Dodge, T., Carteaux, R. and Tuzun, H. (2005), “Making learning fun: quest
Atlantis, a game without guns”, Educational Technology Research and Development, Vol. 53
No. 1, pp. 86-107.
Bang, M., Medin, D. and Atran, S. (2007), “Cultural mosaics and mental models of nature”, Proceedings
of the National Academy of Sciences of the United States of America, Vol. 104 No. 35,
pp. 13868-13874.
Blikstein, P. (2008), “Travels in Troy with Freire: technology as an agent for emancipation”, in Noguera,
P. and Torres, C. (Eds), Social Justice Education for Teachers: Paulo Freire and the Possible
Dream, Sense, Rotterdam, pp. 205-244.
Blikstein, P. (2014), “Bifocal modeling: Promoting authentic scientiﬁc inquiry through exploring and
comparing real and ideal systems linked in real-time”, in Nijholt, A. (Ed.), Playful User Interfaces,
Springer, Singapore, pp. 317-352.
Bogost, I. (2006a), Unit Operations: An Approach to Videogame Criticism, MIT Press, Cambridge,
MA.
Bogost, I. (2006b), “Videogames and ideological frames”, Popular Communication, Vol. 4 No. 3, pp. 165-183.
Bogost, I. (2007), Persuasive Games: The Expressive Power of Videogames, MIT Press, Cambridge, MA.
Brooke, C. (2009), Lingua Fracta: Toward a Rhetoric of New Media, Hampton Press, New York, NY.
Charmaz, K. (1996), “Grounded theory”, in Smith, J., Harré, R. and Van Langenhove, L. (Eds), Rethinking
Methods in Psychology, Sage, London.
Cohen, N. (2017), “Silicon Valley is not your friend: Sunday review”, The New York Times, available at:
https://Nyti.ms/2kLUnZP
Cole, M. and Engeström, Y. (1993), “A cultural-historical approach to distributed cognition”, in
Salomon, G. (Ed.), Distributed Cognitions: Psychological and Educational Considerations,
Cambridge University Press, Cambridge, MA, pp. 1-6.
Collins, A. and Ferguson, W. (1993), “Epistemic forms and epistemic games: Structures and strategies
to guide inquiry”, Educational Psychologist, Vol. 28 No. 1, pp. 25-42.
Collins, A. and Greeno, J. (2011), “Situative view of learning”, Learning and Cognition, Vol. 64.
diSessa, A. (2001), Changing Minds: Computers, Learning, and Literacy, MIT Press, Cambridge, MA.
Emerson, R., Fretz, R. and Shaw, L. (2011), Writing Ethnographic Fieldnotes, University of Chicago
Press, Chicago, IL.
Engelbart, D. (1962), Augmenting Human Intellect: A Conceptual Framework, SRI, Menlo Park.
Fairclough, N. (2004), “Semiotic aspects of social transformation and learning”, in Rogers, R. (Ed.), An
Introduction to Critical Discourse Analysis in Education, Lawrence Erlbaum Associates,
Mahwah, NJ, pp. 225-235.

Gee, J. (2004a), “Discourse analysis: What makes it critical”, in Rogers, R. (Ed.), An Introduction to
Critical Discourse Analysis in Education, Routledge, New York, NY, pp. 19-50.
Gee, J. (2004b), Situated Language and Learning: A Critique of Traditional Schooling, Routledge, New
York, NY.
Glassner, A. (2004), Interactive Storytelling: Techniques for 21st Century Fiction, AK Peters, Natick.
Hansen, M. and Hayles, N. (2000), Embodying Technesis: Technology beyond Writing, University of MI
Press, Ann Arbor, MI.
Haraway, D. (2006), “A cyborg manifesto: Science, technology, and socialist-feminism in the late 20th
century”, in Weiss, J., Nolan, J., Hunsinger, J., Trifonas, P. (Eds), The International Handbook of
Virtual Learning Environments, Springer Netherlands, Dordrecht, pp. 117-158.
Holland, D., Lachicotte, W., Skinner, D. and Cain, C. (2001), Identity and Agency in Cultural Worlds,
Harvard University Press, Cambridge, MA.
Iba, T., Yoshikawa, A. and Munakata, K. (2017), “Philosophy and methodology of clustering in pattern
mining: Japanese anthropologist Jiro Kawakita’s KJ method”, Proceedings of the 24th Conference
on Pattern Languages of Programs, The Hillside Group, p. 12.
Inkle (2016), Ink, Inkle, London, available at: https://github.com/inkle/ink
K-12 Computer Science Framework (2016), available at: www.k12cs.org
Kafai, Y. and Burke, Q. (2013), “The social turn in K-12 programming: moving from computational
thinking to computational participation”, Proceeding of the 44th ACM Technical Symposium on
Computer Science Education - SIGCSE ’13, Denver, CO, p. 603.
Labrande, H. (2011), “Racontons une histoire ensemble: history and characteristics of French IF”, in
Jackson-Mead, K. and Wheeler, J. (Eds), IF Theory Reader, Transcript on Press, Boston, MA,
pp. 389-432.
Lanier, J. (2010), You Are Not a Gadget: A Manifesto, Vintage Books, New York, NY.
Margolis, J. and Fisher, A. (2003), Unlocking the Clubhouse: Women in Computing, MIT Press, Cambridge, MA.
Markoff, J. (2005), What the Dormouse Said: How the Sixties Counterculture Shaped the Personal
Computer Industry, Penguin, London.
Minsky, M. (1988), Society of Mind, Simon and Schuster, New York, NY.
Moll, L.C., Amanti, C., Neff, D. and Gonzalez, N. (1992), “Funds of knowledge for teaching: using a qualitative
approach to connect homes and classrooms”, Theory into Practice, Vol. 31 No. 2, pp. 132-141.
Montfort, N. (2007), “Generating narrative variation in interactive ﬁction”, doctoral thesis, University of
Pennsylvania, Philadelphia.
Morrell, E. (2015), Critical Literacy and Urban Youth: Pedagogies of Access, Dissent, and Liberation,
Routledge, New York, NY.
Murray, J.H. (2017), Hamlet on the Holodeck: The Future of Narrative in Cyberspace, MIT Press,
Cambridge, MA.
Nathan, M.J. and Wagner Alibali, M. (2010), “Learning sciences”, Wiley Interdisciplinary Reviews:
Cognitive Science, Vol. 1 No. 3, pp. 329-345.
Nelson, T.H. (1974), “Computer lib/dream machines”.
NGSS Lead States (2013), Next Generation Science Standards: For States, by States, National
Academies Press, Washington, DC.
Norman, D. (1999), “Affordance, conventions, and design”, Interactions, Vol. 6 No. 3, pp. 38-43.
Ong, W.J. (2013), Orality and Literacy, Routledge, New York, NY.
Papert, S. (1980), Mindstorms: Children, Computers, and Powerful Ideas, Basic Books, New York, NY.
Paris, D. (2011), Language across Difference: Ethnicity, Communication, and Youth Identities in
Changing Urban Schools, Cambridge University Press, Cambridge, MA.

Critical
literacies of
text and code

305

ILS
120,5/6

306

Paris, D. (2012), “Culturally sustaining pedagogy: a needed change in stance, terminology, and
practice”, Educational Researcher, Vol. 41 No. 3, pp. 93-97.
Pea, R. (1985), “Beyond ampliﬁcation: using the computer to reorganize mental functioning”,
Educational Psychologist, Vol. 20 No. 4, pp. 167-182.
Pea, R. (1993), “Practices of distributed intelligence and designs for education”, in Salomon, G. (Ed.),
Distributed Cognitions: Psychological and Educational Considerations, Cambridge University
Press, Cambridge, MA, pp. 47-87.
Proctor, C. (2019), ““Measuring the computational in computational participation: debugging
interactive stories in middle school computer science”, Proceedings of the Thirteenth
International Conference on Computer Supported Collaborative Learning, 17-21 June, Lyon.
Resnick, M., Maloney, J., Monroy-Hernández, A., Rusk, N., Eastmond, E., Brennan, K., Millner, A.,
Rosenbaum, E., Silver, J. and Silverman, B. (2009), “Scratch: programming for all”,
Communications of the ACM, Vol. 52 No. 11, pp. 60-67.
Reyes, A. (2017), Language, Identity, and Stereotype among Southeast Asian American Youth: The
Other Asian, Routledge, New York, NY.
Rosa, J. and Burdick, C. (2016), “Language ideologies”, Oxford Handbook of Language and Society,
Oxford University Press, Oxford, pp. 103-123.
Rosenblatt, L.M. (1968), Literature as Exploration, Noble and Noble, New York, NY.
Ryan, M. (2001), Narrative as Virtual Reality: Immersion and Interactivity in Literature and Electronic
Media, Johns Hopkins University Press, Baltimore, CA.
Scribner, S. and Cole, M. (1978), “Literacy without schooling: testing for intellectual effects”, Harvard
Educational Review, Vol. 48 No. 4, pp. 448-461.
Sipitakiat, A., Blikstein, P. and Cavallo, D. (2004), “GoGo board: augmenting programmable bricks for
economically challenged audiences”, Proceedings of the 6th International Conference on
Learning Sciences, pp. 481-488.
The Design-Based Research Collective (2003), “Design-based research: an emerging paradigm for
educational inquiry”, Educational Researcher, Vol. 32 No. 1, pp. 5-8.
Lorde, A. (2003), “The master’s tools will never dismantle the master’s house”, Feminist Postcolonial
Theory: A Reader, pp. 25-27.
Thomas, S., Joseph, C., Laccetti, J., Mason, B., Mills, S., Perril, S. and Pullinger, K. (2007), “Transliteracy:
crossing divides”, First Monday, Vol. 12 No. 12.
Vossoughi, S. (2014), “Social analytic artifacts made concrete: a study of learning and political
education”, Mind, Culture, and Activity, Vol. 21 No. 4, pp. 353-373.
Vossoughi, S. and Gutiérrez, K. (2016), “Critical pedagogy and sociocultural theory”, Power and
Privilege in the Learning Sciences: Critical and Sociocultural Theories of Learning,
Vygotsky, L. (1980), Mind in Society: The Development of Higher Psychological Processes, Harvard
University Press, Cambridge, MA.
Weintrop, D., Beheshti, E., Horn, M., Orton, K., Jona, K., Trouille, L. and Wilensky, U. (2016), “Deﬁning
computational thinking for mathematics and science classrooms”, Journal of Science Education
and Technology, Vol. 25 No. 1, pp. 127-147.
Wilensky, U. (1999), “NetLogo”, available at: http://ccl.northwestern.edu/netlogo
Wilensky, U. and Stroup, W. (1999), “Learning through participatory simulations: network-based
design for systems learning in classrooms”, Proceedings of the 1999 Conference on Computer
Support for Collaborative Learning, p. 80.
Wysocki, A. (2004), “Opening new media to writing: openings and justiﬁcations”, Wysocki, A.,
Johnson-Eilola, J. and Selfe, C.L. (Eds), Writing New Media: Theory and Applications for
Expanding the Teaching of Composition, UT State University Press, Logan, pp. 1-23.

Further reading
Barthes, R. (2010), “From work to text”, in Leitch, V. and Cain, W. (Eds), The Novel: An Anthology of
Criticism and Theory, 1900-2000, Blackwell Publishing, Malden, pp. 236-241.
Bogost, I. and Losh, E. (2017), “Rhetoric and digital media”, in MacDonald, M. (Ed.), The Oxford
Handbook of Rhetorical Studies, Oxford University Press, Oxford.
Case, N. (2014), “Coming out simulator”, available at: https://ncase.itch.io/coming-out-simulator-2014
Fairclough, N. (1992), “Discourse and text: linguistic and intertextual analysis within discourse
analysis”, Discourse and Society, Vol. 3 No. 2, pp. 193-217.
Freire, P. (2018), Pedagogy of the Oppressed, Bloomsbury Publishing, New York, NY.
Garcia, A., Mirra, N., Morrell, E., Martinez, A. and Scorza, D. (2015), “The council of youth research:
critical literacy and civic agency in the digital age”, Reading and Writing Quarterly, Vol. 31
No. 2, pp. 151-167.
Gee, J. (2008), Social Linguistics and Literacies: Ideology in Discourses, 3rd ed., Routledge, New York, NY.
Graff, G. and Birkenstein, C. (2006), They Say, I Say: The Moves That Matter in Academic Writing,
Norton, New York, NY.
Inkle Studios (2014), 80 Days, Inkle Studios, London.
Koschmann, T., Stahl, G. and Zemel, A. (2004), “The video analyst’s manifesto (or the implications of
Garﬁnkel’s policies for the development of a program of video analytic research within the learning
sciences)”, Proceedings of the 6th International Conference on Learning Sciences, pp. 278-285.
Margolis, J. (2008), Stuck in the Shallow End: Education, Race, and Computing, MIT Press, Cambridge, MA.
Meyer, M. (2017), What Is Rhetoric?, Oxford University Press, Oxford.
National Research Council (2000), How People Learn: Brain, Mind, Experience, and School, Expanded
Edition, National Academies Press, Washington, DC.
Pea, R. (1994), “Seeing what we build together: distributed multimedia learning environments for
transformative communications”, The Journal of the Learning Sciences, Vol. 3 No. 3, pp. 285-299.
Proctor, C. and Garcia, A. (2019), “Student voices in the digital hubbub”, in Hogg, L. and Stockbridge, K.
(Eds), Giving Student Voice Due Weight: Possibilities and Challenges in USA and New Zealand,
Schwartz, D., Chang, J. and Martin, L. (2008), “Instrumentation and innovation in design experiments:
taking the turn towards efﬁciency”, Handbook of Design Research Methods in Education:
Innovations in Science, Technology, Engineering, and Mathematics Learning and Teaching,
pp. 47-67.
Werner, L., Denner, J., Campe, S. and Kawamoto, D.C. (2012), “The fairy performance assessment:
measuring computational thinking in middle school”, Proceedings of the 43rd ACM Technical
Symposium on Computer Science Education, ACM, pp. 215-220.
Corresponding author
Chris Proctor can be contacted at: cproctor@stanford.edu

For instructions on how to order reprints of this article, please visit our website:
www.emeraldgrouppublishing.com/licensing/reprints.htm
Or contact us for further details: permissions@emeraldinsight.com

Critical
literacies of
text and code

307


